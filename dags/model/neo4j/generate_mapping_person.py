#!/usr/bin/env python
# -*- coding: utf-8 -*-


import airflow
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.hive_operator import HiveOperator
from datetime import timedelta

# -------------------------------------------------------------------------------
# these args will get passed on to each operator
# you can override them on a per-task basis during operator initialization

default_args = {
    'owner': 'shensh',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(1),
    'email': [''],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'adhoc':False,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'trigger_rule': u'all_success'
}

# -------------------------------------------------------------------------------
# dag
dag = DAG(
    dag_id='generate_mapping_person',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
    description='generate hive mapping person')

# -------------------------------------------------------------------------------
start = DummyOperator(
    task_id='start',
    dag=dag
)

# 计算全量mapping_person映射表
compute_mapping_person_total = HiveOperator(
    task_id='compute-mapping-person-total',
    hql='''
        insert overwrite table enterprises.hive_mapping_person
        select *
        from enterprises.hive_bd_mapping_person;
        ''',
    dag=dag
)

# 抽取人名去重关系表
extract_mapping_person_relation = HiveOperator(
    task_id='extract-mapping-person-relation',
    hql='''
        insert overwrite table enterprises.hive_mapping_person
        select uid, uid_mapped 
        from enterprises.hive_bd_mapping_person;
        ''',
    dag=dag
)

end = DummyOperator(
    task_id='end',
    dag=dag
)

# -------------------------------------------------------------------------------
start.set_downstream(compute_mapping_person_total)
compute_mapping_person_total.set_downstream(extract_mapping_person_relation)
extract_mapping_person_relation.set_downstream(end)
