import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import Dashboard from '../src/components/Dashboard.vue';

// Example: test Vue component rendering

describe('Dashboard.vue', () => {
  it('renders the Dashboard component', () => {
    const wrapper = mount(Dashboard);
    expect(wrapper.exists()).toBe(true);
  });
});
