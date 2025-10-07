import { mount } from '@vue/test-utils'
import App from '../src/App.vue'

it('renders Bonjour greeting', () => {
  const wrapper = mount(App)
  expect(wrapper.html()).toContain('Bonjour')
})
