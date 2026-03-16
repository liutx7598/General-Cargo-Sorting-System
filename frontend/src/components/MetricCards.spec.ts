import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import MetricCards from './MetricCards.vue';

describe('MetricCards', () => {
  it('renders labels and formatted values', () => {
    const wrapper = mount(MetricCards, {
      props: {
        cards: [
          { label: 'GM', value: 1.42 },
          { label: '状态', value: 'PASS' },
        ],
      },
    });

    expect(wrapper.text()).toContain('GM');
    expect(wrapper.text()).toContain('1.42');
    expect(wrapper.text()).toContain('PASS');
  });
});

