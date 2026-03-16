export function formatShipType(shipType?: string) {
  const shipTypeMap: Record<string, string> = {
    GENERAL_CARGO: '件杂货船',
  };
  return shipType ? (shipTypeMap[shipType] ?? shipType) : '-';
}

export function formatCargoCategory(category?: string) {
  const categoryMap: Record<string, string> = {
    STEEL: '钢材',
    TIMBER: '木材',
    EQUIPMENT: '设备',
    PROJECT: '工程货',
    PIPE: '管材',
    DANGEROUS: '危险货',
  };
  return category ? (categoryMap[category] ?? category) : '-';
}

export function formatStatus(status?: string) {
  const statusMap: Record<string, string> = {
    DRAFT: '草稿',
    GENERATED: '已生成',
    PENDING: '待处理',
    PLANNING: '规划中',
    PLACED: '已摆放',
    UNPLACED: '未摆放',
  };
  return status ? (statusMap[status] ?? status) : '-';
}

export function formatCompliance(status?: string) {
  const complianceMap: Record<string, string> = {
    PASS: '通过',
    FAIL: '不通过',
    PENDING: '待判定',
  };
  return status ? (complianceMap[status] ?? status) : '-';
}

export function formatSeverity(severity?: string) {
  const severityMap: Record<string, string> = {
    ERROR: '严重',
    WARNING: '告警',
  };
  return severity ? (severityMap[severity] ?? severity) : '-';
}

export function formatNumber(value?: number | null, digits = 2) {
  return value == null ? '-' : value.toFixed(digits);
}

export function formatPercent(value?: number | null, digits = 1) {
  return value == null ? '-' : `${(value * 100).toFixed(digits)}%`;
}
