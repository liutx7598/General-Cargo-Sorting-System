CREATE TABLE ship (
    id BIGSERIAL PRIMARY KEY,
    ship_code VARCHAR(64) NOT NULL UNIQUE,
    ship_name VARCHAR(128) NOT NULL,
    ship_type VARCHAR(64) NOT NULL,
    length_overall DOUBLE PRECISION NOT NULL,
    length_between_perpendiculars DOUBLE PRECISION NOT NULL,
    beam DOUBLE PRECISION NOT NULL,
    depth DOUBLE PRECISION NOT NULL,
    lightship_weight DOUBLE PRECISION NOT NULL,
    lightship_kg DOUBLE PRECISION NOT NULL,
    lightship_lcg DOUBLE PRECISION NOT NULL,
    lightship_tcg DOUBLE PRECISION NOT NULL DEFAULT 0,
    design_displacement DOUBLE PRECISION NOT NULL,
    design_gm DOUBLE PRECISION NOT NULL,
    remark TEXT
);

CREATE TABLE hold (
    id BIGSERIAL PRIMARY KEY,
    ship_id BIGINT NOT NULL REFERENCES ship(id) ON DELETE CASCADE,
    hold_no VARCHAR(32) NOT NULL,
    length DOUBLE PRECISION NOT NULL,
    width DOUBLE PRECISION NOT NULL,
    height DOUBLE PRECISION NOT NULL,
    volume DOUBLE PRECISION NOT NULL,
    lcg DOUBLE PRECISION NOT NULL,
    tcg DOUBLE PRECISION NOT NULL,
    vcg DOUBLE PRECISION NOT NULL,
    max_load_weight DOUBLE PRECISION NOT NULL,
    deck_strength_limit DOUBLE PRECISION NOT NULL,
    sequence_no INTEGER NOT NULL,
    remark TEXT,
    CONSTRAINT uk_hold_ship_no UNIQUE (ship_id, hold_no)
);

CREATE TABLE ship_hydrostatic (
    id BIGSERIAL PRIMARY KEY,
    ship_id BIGINT NOT NULL REFERENCES ship(id) ON DELETE CASCADE,
    displacement DOUBLE PRECISION NOT NULL,
    km_value DOUBLE PRECISION NOT NULL,
    draft DOUBLE PRECISION NOT NULL,
    note TEXT
);

CREATE TABLE cargo (
    id BIGSERIAL PRIMARY KEY,
    cargo_code VARCHAR(64) NOT NULL UNIQUE,
    cargo_name VARCHAR(128) NOT NULL,
    cargo_category VARCHAR(64) NOT NULL,
    dangerous_class VARCHAR(32),
    incompatible_tags VARCHAR(255),
    isolation_level DOUBLE PRECISION NOT NULL DEFAULT 0,
    segregation_code INTEGER,
    weight DOUBLE PRECISION NOT NULL,
    length DOUBLE PRECISION NOT NULL,
    width DOUBLE PRECISION NOT NULL,
    height DOUBLE PRECISION NOT NULL,
    stackable BOOLEAN NOT NULL DEFAULT TRUE,
    rotatable BOOLEAN NOT NULL DEFAULT TRUE,
    center_offset_x DOUBLE PRECISION NOT NULL DEFAULT 0,
    center_offset_y DOUBLE PRECISION NOT NULL DEFAULT 0,
    center_offset_z DOUBLE PRECISION NOT NULL DEFAULT 0,
    remark TEXT
);

CREATE TABLE voyage (
    id BIGSERIAL PRIMARY KEY,
    voyage_no VARCHAR(64) NOT NULL UNIQUE,
    ship_id BIGINT NOT NULL REFERENCES ship(id) ON DELETE CASCADE,
    route_info VARCHAR(255),
    departure_port VARCHAR(64),
    arrival_port VARCHAR(64),
    eta TIMESTAMP,
    etd TIMESTAMP,
    status VARCHAR(32) NOT NULL
);

CREATE TABLE stowage_plan (
    id BIGSERIAL PRIMARY KEY,
    voyage_id BIGINT NOT NULL REFERENCES voyage(id) ON DELETE CASCADE,
    plan_no VARCHAR(64) NOT NULL UNIQUE,
    plan_version INTEGER NOT NULL,
    status VARCHAR(32) NOT NULL,
    total_cargo_weight DOUBLE PRECISION NOT NULL DEFAULT 0,
    displacement DOUBLE PRECISION NOT NULL DEFAULT 0,
    kg DOUBLE PRECISION NOT NULL DEFAULT 0,
    lcg DOUBLE PRECISION NOT NULL DEFAULT 0,
    tcg DOUBLE PRECISION NOT NULL DEFAULT 0,
    gm DOUBLE PRECISION NOT NULL DEFAULT 0,
    compliance_status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    warning_count INTEGER NOT NULL DEFAULT 0,
    remark TEXT
);

CREATE TABLE stowage_item (
    id BIGSERIAL PRIMARY KEY,
    plan_id BIGINT NOT NULL REFERENCES stowage_plan(id) ON DELETE CASCADE,
    cargo_id BIGINT NOT NULL REFERENCES cargo(id) ON DELETE RESTRICT,
    hold_id BIGINT NOT NULL REFERENCES hold(id) ON DELETE RESTRICT,
    layer_no INTEGER NOT NULL,
    orientation VARCHAR(16) NOT NULL,
    origin_x DOUBLE PRECISION NOT NULL,
    origin_y DOUBLE PRECISION NOT NULL,
    origin_z DOUBLE PRECISION NOT NULL,
    placed_length DOUBLE PRECISION NOT NULL,
    placed_width DOUBLE PRECISION NOT NULL,
    placed_height DOUBLE PRECISION NOT NULL,
    centroid_x DOUBLE PRECISION NOT NULL,
    centroid_y DOUBLE PRECISION NOT NULL,
    centroid_z DOUBLE PRECISION NOT NULL,
    status VARCHAR(32) NOT NULL,
    violation_flags TEXT
);

CREATE TABLE rule_template (
    id BIGSERIAL PRIMARY KEY,
    rule_code VARCHAR(64) NOT NULL UNIQUE,
    rule_name VARCHAR(128) NOT NULL,
    rule_type VARCHAR(64) NOT NULL,
    expression_json TEXT NOT NULL,
    severity VARCHAR(16) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE warning_record (
    id BIGSERIAL PRIMARY KEY,
    plan_id BIGINT NOT NULL REFERENCES stowage_plan(id) ON DELETE CASCADE,
    cargo_id BIGINT REFERENCES cargo(id) ON DELETE SET NULL,
    hold_id BIGINT REFERENCES hold(id) ON DELETE SET NULL,
    warning_type VARCHAR(64) NOT NULL,
    warning_message TEXT NOT NULL,
    severity VARCHAR(16) NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_hold_ship_id ON hold(ship_id);
CREATE INDEX idx_hydrostatic_ship_id ON ship_hydrostatic(ship_id, displacement);
CREATE INDEX idx_voyage_ship_id ON voyage(ship_id);
CREATE INDEX idx_plan_voyage_id ON stowage_plan(voyage_id);
CREATE INDEX idx_item_plan_id ON stowage_item(plan_id);
CREATE INDEX idx_item_plan_hold ON stowage_item(plan_id, hold_id);
CREATE INDEX idx_warning_plan_id ON warning_record(plan_id);

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
    id, cargo_code, cargo_name, cargo_category, dangerous_class, incompatible_tags, isolation_level, segregation_code,
    weight, length, width, height, stackable, rotatable, center_offset_x, center_offset_y, center_offset_z, remark
) VALUES
    (11, 'CG-001', '普通钢卷 A', 'STEEL', NULL, '', 0.0, NULL, 30.5, 6.0, 2.4, 2.2, TRUE, TRUE, 0.0, 0.0, 0.0, '普通钢材'),
    (12, 'CG-002', '普通钢卷 B', 'STEEL', NULL, '', 0.0, NULL, 28.0, 5.8, 2.3, 2.1, TRUE, TRUE, 0.0, 0.0, 0.0, '普通钢材'),
    (13, 'CG-003', '型钢束', 'STEEL', NULL, '', 0.0, NULL, 24.0, 8.0, 1.8, 1.6, TRUE, TRUE, 0.0, 0.0, 0.0, '钢材'),
    (14, 'CG-004', '木材包 A', 'TIMBER', NULL, 'SPARK', 1.5, NULL, 18.0, 7.0, 2.2, 2.4, TRUE, TRUE, 0.0, 0.0, 0.0, '木材'),
    (15, 'CG-005', '木材包 B', 'TIMBER', NULL, 'SPARK', 1.5, NULL, 16.5, 6.5, 2.2, 2.2, TRUE, TRUE, 0.0, 0.0, 0.0, '木材'),
    (16, 'CG-006', '设备箱 A', 'EQUIPMENT', NULL, '', 0.0, NULL, 40.0, 4.0, 3.2, 3.0, FALSE, TRUE, 0.0, 0.0, 0.0, '设备箱'),
    (17, 'CG-007', '设备箱 B', 'EQUIPMENT', NULL, '', 0.0, NULL, 35.0, 4.5, 3.0, 2.8, FALSE, TRUE, 0.0, 0.0, 0.0, '设备箱'),
    (18, 'CG-008', '危险品包装货', 'DANGEROUS', '3', 'SPARK', 3.0, 2, 12.0, 3.0, 2.5, 2.4, FALSE, TRUE, 0.0, 0.0, 0.0, '包装危险货，隔离等级 2'),
    (19, 'CG-009', '机械备件', 'PROJECT', NULL, '', 0.0, NULL, 22.0, 5.0, 2.5, 2.0, TRUE, TRUE, 0.0, 0.0, 0.0, '工程备件'),
    (20, 'CG-010', '管束', 'PIPE', NULL, '', 0.0, NULL, 14.0, 9.0, 1.5, 1.5, TRUE, TRUE, 0.0, 0.0, 0.0, '长件货');

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

SELECT setval('ship_id_seq', (SELECT MAX(id) FROM ship));
SELECT setval('hold_id_seq', (SELECT MAX(id) FROM hold));
SELECT setval('ship_hydrostatic_id_seq', (SELECT MAX(id) FROM ship_hydrostatic));
SELECT setval('cargo_id_seq', (SELECT MAX(id) FROM cargo));
SELECT setval('voyage_id_seq', (SELECT MAX(id) FROM voyage));
SELECT setval('stowage_plan_id_seq', (SELECT MAX(id) FROM stowage_plan));
SELECT setval('rule_template_id_seq', (SELECT MAX(id) FROM rule_template));
