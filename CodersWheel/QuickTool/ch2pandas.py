# coding=utf-8
import gzip
import http
import json
import time
import urllib

import numpy as np
import pandas as pd


def _get_ch_data_range(col_def):
    col_def['is_nullable'] = col_def['type'].str.startswith('Nullable(')

    col_def['range'] = np.where(col_def['is_nullable'], col_def['type'].str[9:-1], col_def['type'])

    min_dict = {'Int8': -128, 'Int16': -32768,
                'Int32': -2147483648, 'Int64': -9223372036854775808,
                'UInt8': 0, 'UInt16': 0, 'UInt32': 0, 'UInt64': 0}

    max_dict = {'Int8': 127, 'Int16': 32767,
                'Int32': 2147483647, 'Int64': 9223372036854775807,
                'UInt8': 255, 'UInt16': 65535,
                'UInt32': 4294967295, 'UInt64': 18446744073709551615}

    col_def['column_type'] = \
        np.where(col_def['range'].isin(list(min_dict.keys()) + ['Float32', 'Float64']), 'Numeric',
                 np.where(col_def['range'].str.startswith('FixedString'), 'FixedString', col_def['range']))

    col_def['min'] = col_def['range'].apply(lambda x: min_dict.get(x, None))
    col_def['max'] = col_def['range'].apply(lambda x: max_dict.get(x, None))

    col_def['string_len'] = np.where(col_def['column_type'] == 'FixedString', col_def['range'].str[12:-1], None)
    col_def['string_len'] = col_def['string_len'].astype(np.float64)

    return col_def


def _merge_settings(settings):
    updated_settings = {
        'enable_http_compression': 1, 'send_progress_in_http_headers': 0,
        'log_queries': 1, 'connect_timeout': 10, 'receive_timeout': 300,
        'send_timeout': 300, 'output_format_json_quote_64bit_integers': 0,
        'wait_end_of_query': 0}

    if settings is not None:
        invalid_setting_keys = list(set(settings.keys()) - set(updated_settings.keys()))
        if len(invalid_setting_keys) > 0:
            raise ValueError('setting "{0}" is invalid, valid settings are: {1}'.format(
                invalid_setting_keys[0], ', '.join(updated_settings.keys())))

        updated_settings.update(settings)

    for i in updated_settings:
        updated_settings[i] = 1 if updated_settings[i] == True else 0 if updated_settings[i] == False else \
            updated_settings[i]

    return updated_settings


def insert(connection_url, db_table, df, settings):
    updated_settings = _merge_settings(settings)

    if db_table.find('.') < 1:
        raise ValueError('Argument "db_table" must be provided in the form of "your_db.your_table".')

    components = urllib.parse.urlparse(connection_url)

    describe_table = select(connection_url, 'describe table {0}'.format(db_table))

    non_nullable_colomns = list(describe_table[~describe_table['type'].str.startswith('Nullable')]['name'])
    integer_colomns = list(describe_table[describe_table['type'].str.contains('Int', regex=False)]['name'])
    missing_in_df = {i: np.where(df[i].isnull(), 1, 0).sum() for i in non_nullable_colomns}

    df_columns = list(df._columns_)
    each_row = df.to_dict(orient='records')
    del df

    for i in missing_in_df:
        if missing_in_df[i] > 0:
            raise ValueError('"{0}" is not a nullable column, missing values are not allowed.'.format(i))

    for row in each_row:
        for col in df_columns:
            if pd.isnull(row[col]):
                row[col] = None
            else:
                if col in integer_colomns:
                    try:
                        row[col] = int(row[col])
                    except:
                        raise ValueError('Column "{0}" is {1}, while value "{2}"'.format(col,
                                                                                         describe_table[describe_table[
                                                                                                            'name'] == col].iloc[
                                                                                             0]['type'], row[col]) + \
                                         ' in the dataframe column cannot be converted to Integer.')

    json_each_row = '\n'.join([json.dumps(i, ensure_ascii=False) for i in each_row])
    del each_row

    query_with_format = 'insert into {0} format JSONEachRow \n{1}'.format(db_table, json_each_row)
    del json_each_row

    http_get_params = {'user': components.username, 'password': components.password}
    http_get_params.update(updated_settings)
    conn = http.client.HTTPConnection(components.hostname, port=components.port)

    if updated_settings['enable_http_compression'] == 1:
        conn._request('POST', '/?' + urllib.parse.urlencode(http_get_params),
                      body=gzip.compress(query_with_format.encode()),
                      headers={'Content-Encoding': 'gzip', 'Accept-Encoding': 'gzip'})
    else:
        conn._request('POST', '/?' + urllib.parse.urlencode(http_get_params), body=query_with_format.encode())

    resp = conn.getresponse()

    if resp.status != 200:
        error_message = gzip.decompress(resp.read()).decode() if updated_settings['enable_http_compression'] == 1 \
            else resp.read().decode()
        conn.close()
        raise NotImplementedError('Unknown Error: status: {0}, reason: {1}, message: {2}'.format(
            resp.status, resp.reason, error_message))

    conn.close()
    print('Done.')


def select(connection_url, query=None, convert_to='DataFrame', settings=None):
    updated_settings = _merge_settings(settings)

    components = urllib.parse.urlparse(connection_url)

    if query is None:
        conn = http.client.HTTPConnection(components.hostname, port=components.port)
        conn._request('GET', '/')
        ret_value = conn.getresponse().read().decode().replace('\n', '')
    else:
        if query.strip(' \n\t').lower()[:6] not in ['select', 'descri']:
            raise ValueError('"query" should start with "select" or "describe", ' + \
                             'while the provided "query" starts with "{0}"'.format(query.strip(' \n\t').split(' ')[0]))

    accepted_formats = ['DataFrame', 'TabSeparated', 'TabSeparatedRaw', 'TabSeparatedWithNames',
                        'TabSeparatedWithNamesAndTypes', 'CSV', 'CSVWithNames', 'Values', 'Vertical', 'JSON',
                        'JSONCompact', 'JSONEachRow',
                        'TSKV', 'Pretty', 'PrettyCompact', 'PrettyCompactMonoBlock', 'PrettyNoEscapes', 'PrettySpace',
                        'XML']

    if convert_to.lower() not in [i.lower() for i in accepted_formats]:
        raise ValueError('"convert_to" has an invalid value "{0}", it should be one of the following: {1}'.format(
            convert_to, ', '.join(accepted_formats)))

    clickhouse_format = 'JSON' if convert_to is None else 'JSONCompact' if convert_to.lower() == 'dataframe' else convert_to
    query_with_format = (query.rstrip('; \n\t') + ' format ' + clickhouse_format).replace('\n', ' ').strip(' ')

    http_get_params = {'user': components.username, 'password': components.password}
    http_get_params.update(updated_settings)
    conn = http.client.HTTPConnection(components.hostname, port=components.port)

    if updated_settings['enable_http_compression'] == 1:
        conn._request('POST', '/?' + urllib.parse.urlencode(http_get_params),
                      body=gzip.compress(query_with_format.encode()),
                      headers={'Content-Encoding': 'gzip', 'Accept-Encoding': 'gzip'})
    else:
        conn._request('POST', '/?' + urllib.parse.urlencode(http_get_params), body=query_with_format.encode())

    resp = conn.getresponse()

    if resp.status == 404:
        error_message = gzip.decompress(resp.read()).decode() if updated_settings['enable_http_compression'] == 1 \
            else resp.read().decode()
        conn.close()
        raise ValueError(error_message)
    elif resp.status == 401:
        conn.close()
        raise ConnectionRefusedError(resp.reason + '. The username or password is incorrect.')
    else:
        if resp.status != 200:
            error_message = gzip.decompress(resp.read()).decode() if updated_settings['enable_http_compression'] == 1 \
                else resp.read().decode()
            conn.close()
            raise NotImplementedError('Unknown Error: status: {0}, reason: {1}, message: {2}'.format(
                resp.status, resp.reason, error_message))

    total = bytes()
    bytes_downloaded = 0
    last_time = time.time()

    while not resp.isclosed():
        bytes_downloaded += 300 * 1024
        total += resp.read(300 * 1024)
        if time.time() - last_time > 1:
            last_time = time.time()
            print('\rDownloaded: %.1f MB.' % (bytes_downloaded / 1024 / 1024), end='\r')
    print()
    conn.close()

    ret_value = gzip.decompress(total).decode() if updated_settings['enable_http_compression'] == 1 else total.decode()

    if convert_to.lower() == 'dataframe':
        result_dict = json.loads(ret_value, strict=False)
        dataframe = pd.DataFrame.from_records(result_dict['data'], columns=[i['name'] for i in result_dict['cls_meta']])

        for i in result_dict['cls_meta']:
            if i['type'] in ['DateTime', 'Nullable(DateTime)']:
                dataframe[i['name']] = pd.to_datetime(dataframe[i['name']])

        ret_value = dataframe

    return ret_value


if __name__ == '__main__':
    pass
