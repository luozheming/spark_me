#!/usr/bin/env python
# -*- coding: utf-8 -*-




import airflow
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.hive_operator import HiveOperator
from airflow.operators.sensors import ExternalTaskSensor
from datetime import timedelta
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
print sys.getdefaultencoding()

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
    dag_id='generate_neo4j_data',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
    description='extract gs relation')

# -------------------------------------------------------------------------------
# 添加上游依赖 -- enterprise_risk
es_enterprise_risk = ExternalTaskSensor(
    task_id='up-dependent-enterprise-risk',
    external_dag_id='enterprise_risk',
    external_task_id='end',
    trigger_rule='all_done',
    dag=dag
)

# 添加上游依赖 -- gs_relation
es_gs_relation = ExternalTaskSensor(
    task_id='up-dependent-gs-relation',
    external_dag_id='gs_relation',
    external_task_id='end',
    trigger_rule='all_done',
    dag=dag
)

# 添加上游依赖 -- mapping_person
es_mapping_person = ExternalTaskSensor(
    task_id='up-dependent-mapping-person',
    external_dag_id='generate_mapping_person',
    external_task_id='end',
    trigger_rule='all_done',
    dag=dag
)

start = DummyOperator(
    task_id='start',
    dag=dag
)

# 汇总neo4j节点输入表
merge_neo4j_node_input = HiveOperator(
    task_id='merge-neo4j-node-input',
    hql='''
        insert overwrite table enterprises.hive_neo4j_node_input
        select a.uid as uid, a.name as name, a.type as type, 
            case when b.has_risk is not null then b.has_risk else "" end as has_risk,
            unix_timestamp(current_timestamp()) as last_update_time
        from enterprises.hive_neo4j_node a 
        left outer join enterprises.hive_enterprise_risk b on a.uid = b.eid;
        ''',
    dag=dag
)

# 汇总neo4j关系输入表
merge_neo4j_relation_input = HiveOperator(
    task_id='merge-neo4j-relation-input',
    hql='''
        insert overwrite table enterprises.hive_neo4j_relation_input 
        select *
        from enterprises.hive_neo4j_gs_relation;
        ''',
    dag=dag
)

# 人名去重关系
neo4j_mapping_person_input = HiveOperator(
    task_id='neo4j-mapping-person-input',
    hql='''
        insert overwrite table enterprises.hive_neo4j_mapping_person_input 
        select a.*
        from enterprises.hive_mapping_person a 
        left outer join enterprises.hive_neo4j_node b on a.uid = b.uid
        left outer join enterprises.hive_neo4j_node c on a.uid_mapped = c.uid
        where b.uid is not null and c.uid is not null and a.uid != a.uid_mapped;
        ''',
    dag=dag
)

end = DummyOperator(
    task_id='end',
    dag=dag
)

# -------------------------------------------------------------------------------
es_enterprise_risk.set_downstream(start)
es_gs_relation.set_downstream(start)
es_mapping_person.set_downstream(start)
start.set_downstream(merge_neo4j_node_input)
start.set_downstream(merge_neo4j_relation_input)
start.set_downstream(neo4j_mapping_person_input)
merge_neo4j_node_input.set_downstream(end)
merge_neo4j_relation_input.set_downstream(end)
neo4j_mapping_person_input.set_downstream(end)
