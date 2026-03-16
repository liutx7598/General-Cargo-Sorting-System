# 基于专利 CN120874086A 的系统优化说明

## 1. 参考专利

- 文件路径：
  [CN12087..6A.pdf](C:/Users/Administrator/Documents/xwechat_files/wxid_5hj4xtga56h221_2aa2/msg/file/2026-03/CN12087..6A.pdf)
- 专利名称：一种杂货船配载辅助新系统
- 申请人：大连海事大学

本说明用于记录该专利对当前“件杂货智能配载系统”的启发，以及本轮已经实际落地到代码中的优化内容。

## 2. 专利中最有价值的技术点

从专利摘要、权利要求和说明书中，可提炼出以下与当前系统高度相关的技术点：

1. 货物位置不应只停留在表格层面，而应形成真实可视化配载图。
2. 配载核算应基于货物的真实摆位坐标，而不是简单使用货舱舱容中心近似。
3. 对危险货和互抵杂货应支持自动忌装、隔离等级、隔离距离判断。
4. 系统应具备跨船型的通用化能力，而非只适配单船专用。
5. 配载核算不仅包括重心与 GM，还应考虑舱容比、强度与配载均衡性。
6. 配载流程应体现“货舱推荐范围 -> 用户选舱/系统选舱 -> 层空间判断 -> 自动提示换层或换舱”的交互逻辑。

## 3. 优化前系统与专利思路的差距

在本轮优化前，系统虽然已经实现了分舱、摆位、GM、规则校验和二维/三维可视化，但仍存在三个明显差距：

### 3.1 整船重心计算仍有局部坐标近似问题

原系统的 `calculate_ship_centroid()` 直接使用了货物在“货舱局部坐标系”中的 `centroid_x / centroid_y / centroid_z` 参与整船力矩计算。  
这会导致：

- `LCG / TCG / KG` 偏离真实整船坐标
- `Ix` 纵向集中指标也带有坐标系误差

而专利明确强调：需要把货舱内货物合重心转换到整船坐标后再核算。

### 3.2 隔离规则仍偏向“统一距离”，缺少专利中的等级语义

原系统主要支持：

- 不兼容标签
- 通用最小隔离距离

但专利中给出了更明确的隔离等级语义：

- 等级 1：至少 3m 距离
- 等级 2：不同舱
- 等级 3：至少隔一个完整舱
- 等级 4：至少隔一个完整舱且满足更强纵向隔离

这类规则不应只在最终校验时判断，更应进入分舱阶段作为组合约束。

### 3.3 隔离等级没有贯穿前后端数据链

原系统前端、后端和算法服务之间没有专门的 `segregationCode` 字段，因此即便算法侧支持更精细的规则，用户也无法从界面录入。

## 4. 本轮已完成的核心优化

## 4.1 优化一：整船重心改为基于整船坐标计算

### 优化内容

在
[stability.py](C:/Users/Administrator/Desktop/General%20Cargo%20Sorting%20System/stowage-system/algorithm-service/app/solver/stability.py)
中，新增了货舱局部坐标到整船坐标的转换逻辑：

- `ship_x = hold.lcg - hold.length / 2 + local_x`
- `ship_y = hold.tcg - hold.width / 2 + local_y`
- `ship_z = hold.vcg - hold.height / 2 + local_z`

随后：

- `calculate_ship_centroid()` 改为使用整船坐标参与力矩与重心计算
- `calculate_longitudinal_index_in_ship_coordinates()` 改为使用整船纵向坐标计算 `Ix`
- `plan_service.py` 中的总排水量、LCG、TCG、KG、GM、Ix 核算链路同步切换

### 理论意义

这项改动直接回应了专利中“不能只用舱容中心或局部近似值”的问题，使：

- 整船稳性核算更符合真实物理意义
- 不同货舱之间的纵向分布影响能够真实反映
- 后续强度、剪力、弯矩扩展具备正确坐标基础

### 影响文件

- [stability.py](C:/Users/Administrator/Desktop/General%20Cargo%20Sorting%20System/stowage-system/algorithm-service/app/solver/stability.py)
- [plan_service.py](C:/Users/Administrator/Desktop/General%20Cargo%20Sorting%20System/stowage-system/algorithm-service/app/services/plan_service.py)
- [test_solver_core.py](C:/Users/Administrator/Desktop/General%20Cargo%20Sorting%20System/stowage-system/algorithm-service/tests/test_solver_core.py)

## 4.2 优化二：引入专利风格的隔离等级规则

### 优化内容

在
[rule_checker.py](C:/Users/Administrator/Desktop/General%20Cargo%20Sorting%20System/stowage-system/algorithm-service/app/solver/rule_checker.py)
中，引入了 `SeparationRequirement` 规则对象，并新增：

- `build_separation_requirement()`
- `holds_satisfy_separation()`

支持以下逻辑：

- `segregationCode = 1`：同舱可装，但最小距离不低于 3m
- `segregationCode = 2`：必须不同舱
- `segregationCode = 3`：至少隔一个完整货舱
- `segregationCode = 4`：至少隔一个完整货舱，并满足更强的纵向隔离要求

同时保留原有兼容逻辑：

- 无 `segregationCode` 时，继续兼容现有 `isolationLevel` 距离判定
- 不兼容标签仍会触发 `INCOMPATIBLE`

### 理论意义

这项改动把专利里的“隔离等级”从文本规则转成了可执行规则模型，使系统不再只有“距离约束”，而是具备了“距离 + 货舱级拓扑约束”的组合表达能力。

## 4.3 优化三：将隔离等级约束前移到分舱优化

### 优化内容

在
[hold_allocator.py](C:/Users/Administrator/Desktop/General%20Cargo%20Sorting%20System/stowage-system/algorithm-service/app/solver/hold_allocator.py)
中，隔离等级不再只在最终校验阶段判断，而是被加入 CP-SAT 分舱约束中：

- 若某一对货物在某两个货舱上的组合不满足隔离等级要求
- 则直接添加约束 `x(i,h1) + x(j,h2) <= 1`

这意味着系统会在求解时主动避开违反专利隔离等级的分舱组合，而不是先分配、后报错。

### 理论意义

这是从“事后检查”升级为“求解内生约束”的关键一步，显著提高了：

- 求解结果的可行性
- 规则与优化的一体化程度
- 系统工程可用性

## 4.4 优化四：隔离等级贯穿前后端数据链

### 优化内容

新增 `segregationCode` 字段，并贯穿以下层级：

- 算法服务输入模型  
  [domain.py](C:/Users/Administrator/Desktop/General%20Cargo%20Sorting%20System/stowage-system/algorithm-service/app/models/domain.py)  
  [solver.py](C:/Users/Administrator/Desktop/General%20Cargo%20Sorting%20System/stowage-system/algorithm-service/app/schemas/solver.py)

- 后端实体 / DTO / VO / 算法载荷  
  [Cargo.java](C:/Users/Administrator/Desktop/General%20Cargo%20Sorting%20System/stowage-system/backend/src/main/java/com/stowage/system/entity/Cargo.java)  
  [CargoDtos.java](C:/Users/Administrator/Desktop/General%20Cargo%20Sorting%20System/stowage-system/backend/src/main/java/com/stowage/system/dto/CargoDtos.java)  
  [ViewModels.java](C:/Users/Administrator/Desktop/General%20Cargo%20Sorting%20System/stowage-system/backend/src/main/java/com/stowage/system/vo/ViewModels.java)  
  [AlgorithmModels.java](C:/Users/Administrator/Desktop/General%20Cargo%20Sorting%20System/stowage-system/backend/src/main/java/com/stowage/system/client/AlgorithmModels.java)  
  [EntityMapper.java](C:/Users/Administrator/Desktop/General%20Cargo%20Sorting%20System/stowage-system/backend/src/main/java/com/stowage/system/service/impl/EntityMapper.java)  
  [CargoServiceImpl.java](C:/Users/Administrator/Desktop/General%20Cargo%20Sorting%20System/stowage-system/backend/src/main/java/com/stowage/system/service/impl/CargoServiceImpl.java)

- 前端类型与页面录入  
  [index.ts](C:/Users/Administrator/Desktop/General%20Cargo%20Sorting%20System/stowage-system/frontend/src/types/index.ts)  
  [CargoManagementView.vue](C:/Users/Administrator/Desktop/General%20Cargo%20Sorting%20System/stowage-system/frontend/src/views/CargoManagementView.vue)

- 初始化数据  
  [demo-data.sql](C:/Users/Administrator/Desktop/General%20Cargo%20Sorting%20System/stowage-system/backend/src/main/resources/demo-data.sql)  
  [V1__init_schema_and_data.sql](C:/Users/Administrator/Desktop/General%20Cargo%20Sorting%20System/stowage-system/backend/src/main/resources/db/migration/V1__init_schema_and_data.sql)

### 工程意义

这使“专利规则”从算法能力变成了系统能力，用户可以直接在 UI 中录入隔离等级，再由后端传给算法服务。

## 4.5 优化五：修正并增强合规结论文案

在
[evaluator.py](C:/Users/Administrator/Desktop/General%20Cargo%20Sorting%20System/stowage-system/algorithm-service/app/solver/evaluator.py)
中，重新整理了 PASS / FAIL 原因输出文案，确保：

- 原因中文可读
- 隔离等级违规和距离违规统一纳入合规失败依据

## 5. 本轮优化后的系统能力提升

相较优化前，当前系统新增了以下能力：

1. 总重心与纵向指标基于真实整船坐标计算
2. 危险货 / 特定货对支持隔离等级 1-4 规则
3. 分舱阶段就能规避隔离等级冲突
4. 前后端支持录入和传输隔离等级字段
5. 示例数据中已给危险品包装货补充隔离等级示例

## 6. 已完成验证

已完成如下验证：

- 算法服务测试：
  `20 passed`
- 前端测试：
  `3 passed`
- 前端生产构建：
  `npm run build` 通过
- 后端编译：
  `mvn -q -DskipTests compile` 通过

## 7. 基于专利、但尚未完全落地的后续优化建议

虽然本轮已经落地了最核心的两类专利思路，但仍有三块值得继续推进：

### 7.1 舱容比法进入优化目标

专利明确提出“中部大舱多装、首尾小舱少装”的舱容比法。  
当前系统已有舱容利用率与相邻差异判断，但仍可进一步做成：

- 每舱目标载重推荐值
- 允许偏差范围
- 分舱优化目标中的舱容比偏差惩罚项

### 7.2 货物重量垂向分配比例法

专利强调要控制垂向分布。  
当前系统已经通过“同层聚拢、低层优先、平放优先”间接实现，但后续可进一步量化为：

- 各层重量比例
- 上层重量阈值
- 垂向装载均衡系数

### 7.3 船舶强度核算

专利中对剪力、弯矩和浮力分布有更深入描述。  
当前系统尚未完全实现这部分。建议后续增加：

- 货舱重量纵向分布曲线
- 浮力分布近似
- 剪力 / 弯矩简化计算
- 强度告警

## 8. 结论

本轮优化不是简单“参考了一个专利概念”，而是把专利中最关键的两类方法真正转化为系统代码：

- 用真实整船坐标替代局部近似坐标
- 用隔离等级规则替代单一距离规则

这两项优化直接提升了系统的：

- 理论严谨性
- 稳性核算真实性
- 规则表达能力
- 工程可解释性
- 后续论文论证价值

因此，从论文和系统双重视角看，这一轮优化是一次高价值的“专利驱动型升级”。
