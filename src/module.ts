import { PanelPlugin } from '@grafana/data';
import { SimpleOptions } from './types';
import { SimplePanel } from './components/SimplePanel';

export const plugin = new PanelPlugin<SimpleOptions>(SimplePanel).setPanelOptions((builder) => {
  return builder
    .addTextInput({
      path: 'Address',
      name: 'Address and port for the api',
      description: 'Your address where the API is running to consult for the panel screenshot. Check $ollama serve',
      defaultValue: '127.0.0.1:11434',
    })
    .addTextInput({
      path: 'Model',
      name: 'Model Name',
      description: '',
      defaultValue: 'llama3.2-vision:latest',
    });
});
