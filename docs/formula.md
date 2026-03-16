# 公式说明

## 符号说明

- `li, bi, hi`：货物原始长宽高
- `ai, ci, di`：根据朝向旋转后的摆放尺寸
- `x0_i, y0_i, z0_i`：货物左后下角原点
- `dx_i, dy_i, dz_i`：货物偏心量
- `xi, yi, zi`：单件货物重心
- `Wi`：单件货物重量
- `Vi`：单件货物体积
- `Ln, Bn, Hn, Vn`：第 `n` 个货舱的长、宽、高、容积
- `W0, KG0, Xg0, Yg0`：空船重量与重心参数
- `Delta`：总排水量
- `Xg, Yg, KG`：整船重心
- `KM(Delta)`：按排水量插值得到的静水力 KM
- `GM`：初稳性高度
- `eta_n`：第 `n` 个货舱体积利用率
- `Ix`：纵向集中指标

## 公式关系链

1. 原始尺寸 + 朝向 -> 摆放后尺寸

```text
(li, bi, hi) + orientation -> (ai, ci, di)
```

在代码中由 `rotate_dimensions()` 实现。

2. 摆放原点 + 摆放后尺寸 + 偏心 -> 单件货物重心

```text
xi = x0_i + ai / 2 + dx_i
yi = y0_i + ci / 2 + dy_i
zi = z0_i + di / 2 + dz_i
```

在代码中由 `calculate_cargo_centroid()` 实现。

3. 单件货物重量 + 单件货物重心 -> 货舱合重心

```text
Wn = ΣWi
Xn = Σ(Wi * xi) / Wn
Yn = Σ(Wi * yi) / Wn
Zn = Σ(Wi * zi) / Wn
```

在代码中由 `calculate_hold_centroid()` 实现。

4. 空船参数 + 所有货物参数 -> `Delta, Xg, Yg, KG`

```text
Delta = W0 + ΣWi + fuelWeight + ballastWeight + freshWaterWeight + storesWeight
Xg = (W0 * Xg0 + Σ(Wi * xi) + otherLongMoment) / Delta
Yg = (W0 * Yg0 + Σ(Wi * yi) + otherTranMoment) / Delta
KG = (W0 * KG0 + Σ(Wi * zi) + otherVertMoment) / Delta
```

在代码中由 `calculate_ship_centroid()` 实现，并输出纵向、横向、垂向力矩。

5. `Delta + KG + 静水力表 -> GM`

```text
GM = KM(Delta) - KG - FSC
```

其中 `KM(Delta)` 使用 `interpolate_km()` 对 `ship_hydrostatic` 插值，`calculate_gm()` 负责最终计算。

6. 货物体积 + 货舱容积 -> `eta_n`

```text
Vi = ai * ci * di
eta_n = ΣVi / Vn
lambda_n = Wn / Vn
R_n = |eta_n - eta_(n+1)|
```

在代码中由 `calculate_hold_utilization()` 和 evaluator 聚合。

7. 货物重量分布 -> `Ix`

```text
Ix = Σ(Wi * |xi - Xref|)
```

在代码中由 `calculate_longitudinal_index()` 实现。

8. 所有规则判定结果 + 稳性结果 -> `complianceStatus`

若满足以下条件则 `PASS`，否则 `FAIL`：

- 无越界
- 无碰撞
- 无忌装违规
- 无隔离违规
- `GM >= GM_min`
- `eta_n` 在阈值内
- `R_n` 在阈值内
- `Ix <= Ix_max`

在代码中由 `evaluate_compliance()` 实现。

## 边界约束

```text
0 <= x0_i
x0_i + ai <= Ln
0 <= y0_i
y0_i + ci <= Bn
0 <= z0_i
z0_i + di <= Hn
```

由 `check_bounds()` 实现。

## 不重叠约束

```text
x0_i + ai <= x0_j
or x0_j + aj <= x0_i
or y0_i + ci <= y0_j
or y0_j + cj <= y0_i
or z0_i + di <= z0_j
or z0_j + dj <= z0_i
```

由 `check_overlap()` 取反判断。

## 隔离距离

```text
delta_x = max(0, x0_j - (x0_i + ai), x0_i - (x0_j + aj))
delta_y = max(0, y0_j - (y0_i + ci), y0_i - (y0_j + cj))
delta_z = max(0, z0_j - (z0_i + di), z0_i - (z0_j + dj))
Dist(i,j) = sqrt(delta_x^2 + delta_y^2 + delta_z^2)
Dist(i,j) >= D_ij
```

由 `calculate_distance_between_boxes()` 和 `rule_checker.py` 联合实现。
