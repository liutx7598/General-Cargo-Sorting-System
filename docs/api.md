# 接口说明

## algorithm-service

### `POST /api/solver/generate-plan`

输入完整的船舶、货舱、货物和静水力上下文，返回真实计算后的配载结果、告警和求解指标。

### `POST /api/solver/validate-plan`

对已有配载项重新计算重心、GM、舱容比和规则结果。

### `POST /api/solver/cargo-centroid`

计算单件货物重心。

### `POST /api/solver/hold-centroid`

计算货舱合重心。

### `POST /api/solver/ship-stability`

计算整船总重心、排水量、GM 和力矩。

### `POST /api/solver/rule-check`

执行越界、碰撞、忌装和隔离规则检查。

## backend

### 主数据

- `GET /api/ships`
- `POST /api/ships`
- `GET /api/ships/{id}`
- `POST /api/ships/{id}/holds`
- `GET /api/ships/{id}/holds`
- `GET /api/cargos`
- `POST /api/cargos`
- `GET /api/voyages`
- `POST /api/voyages`

### 配载方案

- `POST /api/plans`
- `GET /api/plans/{id}`
- `GET /api/plans/{id}/items`
- `GET /api/plans/{id}/warnings`
- `POST /api/plans/{id}/generate`
- `POST /api/plans/{id}/validate`

