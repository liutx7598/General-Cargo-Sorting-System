# 总体架构

## 架构概览

系统采用前后端分离加算法独立服务的三层结构：

1. `frontend` 负责录单、任务发起、结果展示、图表和 2.5D/简化 3D 可视化。
2. `backend` 负责主数据管理、航次与配载方案管理、规则模板和告警持久化，并编排算法服务。
3. `algorithm-service` 负责几何计算、重心核算、GM 稳性、规则校验、启发式 + CP-SAT 求解。

## 模块边界

- 前端只通过 REST API 与后端通信，不直接调用算法服务。
- 后端保存船舶、货舱、货物、航次、方案、告警、规则和静水力表。
- 算法服务不访问数据库，只接收完整计算上下文并输出真实计算结果。
- Redis 预留作列表缓存、配载结果缓存和二期任务编排缓冲。

## 调用链

1. 用户在前端创建或选择船舶、航次和货物。
2. 前端调用 `POST /api/plans/{id}/generate`。
3. 后端查询 `ship / hold / cargo / ship_hydrostatic`，组装算法请求。
4. 算法服务按“四阶段”流程执行：
   - 阶段 A：静态筛选
   - 阶段 B：货舱分配
   - 阶段 C：舱内摆位
   - 阶段 D：核算与回退
5. 后端持久化 `stowage_plan / stowage_item / warning_record`。
6. 前端展示 PASS / FAIL、GM、舱容比、告警和可视化结果。

## 关键依赖链

`geometry -> centroid -> hold centroid -> ship centroid -> KM interpolate -> GM -> rule checker -> evaluator -> compliance`

这条链路既体现在 [formula.md](./formula.md)，也体现在算法服务的模块拆分中，避免把所有计算堆进单个函数。

