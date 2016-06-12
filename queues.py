from kombu import Exchange, Queue

task_exchange = Exchange('test_tasks', type='direct')
other_exchange = Exchange('pedQueueEx', type='fanout')
task_queues = [Queue('hipri', task_exchange, routing_key='hipri'),
               Queue('midpri', task_exchange, routing_key='midpri'),
               Queue('lopri', task_exchange, routing_key='lopri'),
               Queue('pedQueue', other_exchange, routing_key='pedQueue')]