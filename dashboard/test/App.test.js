import { mount } from '@vue/test-utils'
import App from '../src/App.vue'

describe('App', () => {
  it('renders Bonjour', () => {
    const wrapper = mount(App)
    expect(wrapper.text()).toContain('Bonjour')
  })
})
