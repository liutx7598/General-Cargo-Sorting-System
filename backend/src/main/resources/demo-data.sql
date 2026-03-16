INSERT INTO ship (
    id, ship_code, ship_name, ship_type, length_overall, length_between_perpendiculars,
    beam, depth, lightship_weight, lightship_kg, lightship_lcg, lightship_tcg,
    design_displacement, design_gm, remark
) VALUES (
    1, 'GC-001', 'M/V Harmony Trader', 'GENERAL_CARGO', 96.0, 90.0,
    16.8, 9.2, 1680.0, 5.5, 47.0, 0.0, 3650.0, 1.6, '示例件杂货船'
);

INSERT INTO hold (
    id, ship_id, hold_no, length, width, height, volume, lcg, tcg, vcg,
    max_load_weight, deck_strength_limit, sequence_no, remark
) VALUES
    (1, 1, 'H1', 17.0, 12.0, 8.0, 1632.0, 19.0, 0.0, 5.0, 420.0, 7.5, 1, '首舱'),
    (2, 1, 'H2', 18.0, 12.6, 8.0, 1814.4, 37.5, 0.0, 5.0, 450.0, 7.8, 2, '前中舱'),
    (3, 1, 'H3', 19.5, 13.0, 8.5, 2154.75, 58.0, 0.0, 5.2, 480.0, 8.0, 3, '后中舱'),
    (4, 1, 'H4', 16.0, 11.8, 7.5, 1416.0, 77.5, 0.0, 4.8, 390.0, 7.2, 4, '尾舱');

INSERT INTO ship_hydrostatic (id, ship_id, displacement, km_value, draft, note) VALUES
    (1, 1, 1600.0, 7.15, 4.5, 'light'),
    (2, 1, 1900.0, 7.45, 4.8, 'sample-1'),
    (3, 1, 2200.0, 7.72, 5.1, 'sample-2'),
    (4, 1, 2600.0, 8.01, 5.5, 'sample-3'),
    (5, 1, 3000.0, 8.24, 5.9, 'sample-4'),
    (6, 1, 3400.0, 8.46, 6.2, 'sample-5'),
    (7, 1, 3800.0, 8.63, 6.5, 'sample-6');

INSERT INTO cargo (
    id, cargo_code, cargo_name, cargo_category, dangerous_class, incompatible_tags, isolation_level,
    weight, length, width, height, stackable, rotatable, center_offset_x, center_offset_y, center_offset_z, remark
) VALUES
    (11, 'CG-001', '普通钢卷 A', 'STEEL', NULL, '', 0.0, 30.5, 6.0, 2.4, 2.2, TRUE, TRUE, 0.0, 0.0, 0.0, '普通钢材'),
    (12, 'CG-002', '普通钢卷 B', 'STEEL', NULL, '', 0.0, 28.0, 5.8, 2.3, 2.1, TRUE, TRUE, 0.0, 0.0, 0.0, '普通钢材'),
    (13, 'CG-003', '型钢束', 'STEEL', NULL, '', 0.0, 24.0, 8.0, 1.8, 1.6, TRUE, TRUE, 0.0, 0.0, 0.0, '钢材'),
    (14, 'CG-004', '木材包 A', 'TIMBER', NULL, 'SPARK', 1.5, 18.0, 7.0, 2.2, 2.4, TRUE, TRUE, 0.0, 0.0, 0.0, '木材'),
    (15, 'CG-005', '木材包 B', 'TIMBER', NULL, 'SPARK', 1.5, 16.5, 6.5, 2.2, 2.2, TRUE, TRUE, 0.0, 0.0, 0.0, '木材'),
    (16, 'CG-006', '设备箱 A', 'EQUIPMENT', NULL, '', 0.0, 40.0, 4.0, 3.2, 3.0, FALSE, TRUE, 0.0, 0.0, 0.0, '设备箱'),
    (17, 'CG-007', '设备箱 B', 'EQUIPMENT', NULL, '', 0.0, 35.0, 4.5, 3.0, 2.8, FALSE, TRUE, 0.0, 0.0, 0.0, '设备箱'),
    (18, 'CG-008', '危险品包装货', 'DANGEROUS', '3', 'SPARK', 3.0, 12.0, 3.0, 2.5, 2.4, FALSE, TRUE, 0.0, 0.0, 0.0, '危险品包装货'),
    (19, 'CG-009', '机械备件', 'PROJECT', NULL, '', 0.0, 22.0, 5.0, 2.5, 2.0, TRUE, TRUE, 0.0, 0.0, 0.0, '工程备件'),
    (20, 'CG-010', '管束', 'PIPE', NULL, '', 0.0, 14.0, 9.0, 1.5, 1.5, TRUE, TRUE, 0.0, 0.0, 0.0, '长件货');

INSERT INTO voyage (
    id, voyage_no, ship_id, route_info, departure_port, arrival_port, eta, etd, status
) VALUES (
    1, 'VY-202603-001', 1, 'Shanghai -> Busan', 'Shanghai', 'Busan',
    '2026-03-18 08:00:00', '2026-03-16 18:00:00', 'PLANNING'
);

INSERT INTO stowage_plan (
    id, voyage_id, plan_no, plan_version, status, total_cargo_weight, displacement,
    kg, lcg, tcg, gm, compliance_status, warning_count, remark
) VALUES (
    1, 1, 'PLAN-20260313-001', 1, 'DRAFT', 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 'PENDING', 0, '示例草稿方案'
);

INSERT INTO rule_template (
    id, rule_code, rule_name, rule_type, expression_json, severity, enabled
) VALUES
    (1, 'RULE-BOUNDARY', '空间越界禁止', 'BOUNDARY', '{"type":"BOUNDARY","enabled":true}', 'ERROR', TRUE),
    (2, 'RULE-OVERLAP', '货物碰撞禁止', 'OVERLAP', '{"type":"OVERLAP","enabled":true}', 'ERROR', TRUE),
    (3, 'RULE-INCOMPATIBLE', '不兼容货物必须隔离', 'INCOMPATIBLE', '{"type":"ISOLATION","defaultDistance":1.0}', 'ERROR', TRUE),
    (4, 'RULE-GM', 'GM 不得低于阈值', 'STABILITY', '{"type":"GM","min":0.5}', 'ERROR', TRUE),
    (5, 'RULE-ADJ-HOLD', '相邻舱利用率差异不得超过阈值', 'BALANCE', '{"type":"ADJACENT_HOLD_DIFF","max":0.4}', 'WARN', TRUE);
ALTER TABLE ship ALTER COLUMN id RESTART WITH 2;
ALTER TABLE hold ALTER COLUMN id RESTART WITH 5;
ALTER TABLE ship_hydrostatic ALTER COLUMN id RESTART WITH 8;
ALTER TABLE cargo ALTER COLUMN id RESTART WITH 21;
ALTER TABLE voyage ALTER COLUMN id RESTART WITH 2;
ALTER TABLE stowage_plan ALTER COLUMN id RESTART WITH 2;
ALTER TABLE stowage_item ALTER COLUMN id RESTART WITH 1;
ALTER TABLE rule_template ALTER COLUMN id RESTART WITH 6;
ALTER TABLE warning_record ALTER COLUMN id RESTART WITH 1;
