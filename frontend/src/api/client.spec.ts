import { describe, expect, it, vi } from 'vitest';

import { unwrap } from './client';

describe('client unwrap', () => {
  it('returns nested api data', async () => {
    const promise = Promise.resolve({
      data: {
        success: true,
        message: 'OK',
        data: { value: 42 },
      },
    });
    await expect(unwrap(promise)).resolves.toEqual({ value: 42 });
  });

  it('keeps promise contract', async () => {
    const promise = vi.fn().mockResolvedValue({
      data: { success: true, message: 'OK', data: ['a'] },
    });
    await unwrap(promise());
    expect(promise).toHaveBeenCalledTimes(1);
  });
});

