# traders

## TODO
1. add Refine Learning

## COMMAND

### 从db生成model 
`python -m pwiz --engine=sqlite traders.db > schema.py
`

### 同步表到db
python models.py

### 修改表结构
python migration.py

### TODO
1. 添加成交日期
2. 继续实验其他模型