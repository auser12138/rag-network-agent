from .db import get_connection
from .config import COLLECTION_NAME

Table = "documents"

#查询文件是否保存
def get_file(source,collection=COLLECTION_NAME):
    conn =get_connection()
    try:
        with conn.cursor()as cur:
            cur.execute(
                f"select *from {Table} where source = %s and collection = %s",
                (source,collection),
            )
            #execute：执行数据库语句；fetchone：从查询的结果拿一条
            return cur.fetchone()
    finally:
        conn.close()
        
#录入文件
def add_file(source,file_hash,chunk_count,collection =COLLECTION_NAME):
    conn = get_connection()
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""insert into {Table} (source,file_hash,chunk_count,collection,status)
                    VALUES (%s, %s, %s, %s,'active')""",
                    (source, file_hash, chunk_count, collection),
            )
            conn.commit()
    finally:
        conn.close()
#更新文件    
def update_file(source,file_hash,chunk_count,collection=COLLECTION_NAME):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""update {Table}
                            set file_hash = %s ,chunk_count = %s, status = 'active'
                            where source= %s and collection = %s""",
                            (file_hash,chunk_count,source,collection),
            )
            conn.commit()
    finally:
        conn.close()

#记录存在的文件
def list_file(collection= COLLECTION_NAME,status = 'active'):
    conn =get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""select source,file_hash,chunk_count,status 
                from {Table} 
                where collection = %s and status =%s
                order by source""",
                (collection,status)
            )
            return cur.fetchall()
    finally:
        conn.close()
    
#记录被标记删除的文件
def deleted_file(source,collection = COLLECTION_NAME):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""update {Table} set status = 'deleted' 
                where source = %s and collection = %s""",
                (source,collection)
            )
            conn.commit()
    finally:
        conn.close()