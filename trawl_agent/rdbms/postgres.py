# !/usr/bin/python
import psycopg2
import trawl_agent.common.api_handler
import time

class PostgresStats():
    query = {
        'size': "SELECT SUM(pg_database_size(datid)) as total_size from pg_stat_database",
        'threads': "SELECT COUNT(*) FROM pg_stat_activity",
        'activeconn': "SELECT SUM(numbackends) FROM pg_stat_database",
        'tupreturned': "SELECT SUM(tup_returned) FROM pg_stat_database",
        'tupfetched': "SELECT SUM(tup_fetched) FROM pg_stat_database",
        'tupinserted': "SELECT SUM(tup_inserted) FROM pg_stat_database",
        'tupupdated': "SELECT SUM(tup_updated) FROM pg_stat_database",
        'tupdeleted': "SELECT SUM(tup_deleted) FROM pg_stat_database",
        'xactcommit': "SELECT SUM(xact_commit) FROM pg_stat_database",
        'xactrollback': "SELECT SUM(xact_rollback) FROM pg_stat_database",
        'exclusivelock': "SELECT COUNT(*) FROM pg_locks WHERE mode='ExclusiveLock'",
        'accessexclusivelock': "SELECT COUNT(*) FROM pg_locks WHERE mode='AccessExclusiveLock'",
        'accesssharelock': "SELECT COUNT(*) FROM pg_locks WHERE mode='AccessShareLock'",
        'rowsharelock': "SELECT COUNT(*) FROM pg_locks WHERE mode='RowShareLock'",
        'rowexclusivelock': "SELECT COUNT(*) FROM pg_locks WHERE mode='RowExclusiveLock'",
        'shareupdateexclusivelock': "SELECT COUNT(*) FROM pg_locks WHERE mode='ShareUpdateExclusiveLock'",
        'sharerowexclusivelock': "SELECT COUNT(*) FROM pg_locks WHERE mode='ShareRowExclusiveLock'",
        'checkpoints_timed': "SELECT checkpoints_timed FROM pg_stat_bgwriter",
        'checkpoints_req': "SELECT checkpoints_req FROM pg_stat_bgwriter",
        'buffers_checkpoint': "SELECT buffers_checkpoint FROM pg_stat_bgwriter",
        'buffers_clean': "SELECT buffers_clean FROM pg_stat_bgwriter",
        'maxwritten_clean': "SELECT maxwritten_clean FROM pg_stat_bgwriter",
        'buffers_backend': "SELECT buffers_backend FROM pg_stat_bgwriter",
        'buffers_alloc': "SELECT buffers_alloc FROM pg_stat_bgwriter"
    }


    def execute_query(self, query, host, port, user, password):
        dbname = 'trawl_io'
        try:
            con = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        except:
            raise
        cur = con.cursor()
        cur.execute(query)
        row = cur.fetchone()
        con.close()
        return row

