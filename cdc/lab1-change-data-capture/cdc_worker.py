import json
import time
import pika
import psycopg2
import psycopg2.extras

# 1. 连接 RabbitMQ
rmq_conn = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="localhost",
        port=5672,
        credentials=pika.PlainCredentials("guest", "guest"),
    )
)
rmq_channel = rmq_conn.channel()

# 声明交换机和队列
rmq_channel.exchange_declare(
    exchange="pg_cdc_exchange", exchange_type="fanout", durable=True
)
rmq_channel.queue_declare(queue="pg_cdc_queue", durable=True)
rmq_channel.queue_bind(exchange="pg_cdc_exchange", queue="pg_cdc_queue")

# 2. 建立 Postgres 逻辑复制连接 (connection_factory 必须为 LogicalReplicationConnection)
pg_conn = psycopg2.connect(
    dbname="mydb",
    user="postgres",
    password="mysecretpassword",
    host="localhost",
    port=5432,
    connection_factory=psycopg2.extras.LogicalReplicationConnection,
)

cur = pg_conn.cursor()
slot_name = "rabbitmq_cdc_slot"


# 3. 定义消息消费回调
def consume_stream(msg):
    # msg.payload 为解码后的变更文本（由 test_decoding 生成）
    raw_payload = msg.payload
    print(f"[Captured CDC Event]: {raw_payload}")

    # 包装为统一的事件格式
    event = {
        "lsn": msg.data_start,
        "payload": raw_payload,
        "timestamp": int(time.time()),
    }

    # 发送到 RabbitMQ
    rmq_channel.basic_publish(
        exchange="pg_cdc_exchange",
        routing_key="",
        body=json.dumps(event),
        properties=pika.BasicProperties(
            delivery_mode=2  # 消息持久化
        ),
    )

    # 确认推进 LSN，释放 Postgres 端的 WAL 日志
    msg.cursor.send_feedback(flush_lsn=msg.data_start)


print("正在监听 Postgres WAL 变更并转发至 RabbitMQ...")
# 启动复制流
cur.start_replication(slot_name=slot_name, decode=True)
cur.consume_stream(consume_stream)
