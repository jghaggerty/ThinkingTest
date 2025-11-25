import type { Severity, ZoneStatus } from '../types';

export const HEURISTIC_LABELS: Record<string, string> = {
  anchoring: 'Anchoring Bias',
  loss_aversion: 'Loss Aversion',
  sunk_cost: 'Sunk Cost Fallacy',
  confirmation_bias: 'Confirmation Bias',
  availability_heuristic: 'Availability Heuristic',
};

export const HEURISTIC_DESCRIPTIONS: Record<string, string> = {
  anchoring: 'Over-reliance on the first piece of information encountered',
  loss_aversion: 'Stronger response to potential losses than equivalent gains',
  sunk_cost: 'Continuing a behavior due to previously invested resources',
  confirmation_bias: 'Favoring information that confirms existing beliefs',
  availability_heuristic: 'Overestimating likelihood based on readily available examples',
};

export const SEVERITY_COLORS: Record<Severity, { bg: string; text: string; border: string }> = {
  low: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
  medium: { bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200' },
  high: { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-200' },
  critical: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
};

export const ZONE_COLORS: Record<ZoneStatus, { bg: string; text: string; border: string }> = {
  green: { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200' },
  yellow: { bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200' },
  red: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
};

export const STATUS_LABELS: Record<string, string> = {
  pending: 'Pending',
  running: 'Running',
  completed: 'Completed',
  failed: 'Failed',
};

export const IMPACT_LABELS: Record<string, string> = {
  low: 'Low Impact',
  medium: 'Medium Impact',
  high: 'High Impact',
};

export const DIFFICULTY_LABELS: Record<string, string> = {
  easy: 'Easy',
  moderate: 'Moderate',
  complex: 'Complex',
};

export const AVAILABLE_HEURISTICS = [
  { value: 'anchoring', label: HEURISTIC_LABELS.anchoring, description: HEURISTIC_DESCRIPTIONS.anchoring },
  { value: 'loss_aversion', label: HEURISTIC_LABELS.loss_aversion, description: HEURISTIC_DESCRIPTIONS.loss_aversion },
  { value: 'sunk_cost', label: HEURISTIC_LABELS.sunk_cost, description: HEURISTIC_DESCRIPTIONS.sunk_cost },
  { value: 'confirmation_bias', label: HEURISTIC_LABELS.confirmation_bias, description: HEURISTIC_DESCRIPTIONS.confirmation_bias },
  { value: 'availability_heuristic', label: HEURISTIC_LABELS.availability_heuristic, description: HEURISTIC_DESCRIPTIONS.availability_heuristic },
];
