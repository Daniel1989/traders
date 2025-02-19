# traders

## TODO
1. add Refine Learning

## COMMAND

### 从db生成model 
`python -m pwiz --engine=sqlite traders.db > schema.py`

### 同步表到db
python models.py

### 修改表结构
python migration.py

### TODO
1. 并行调用

### 依赖的项目
https://github.com/Python3WebSpider/ProxyPool

playwright install

## fastapi
uvicorn app.main:app --reload --port 8080