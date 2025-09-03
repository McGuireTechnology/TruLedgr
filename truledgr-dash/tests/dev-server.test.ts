import { describe, it, expect } from 'vitest';
import { spawn } from 'child_process';

function runDevServer() {
  return new Promise((resolve, reject) => {
    const proc = spawn('npm', ['run', 'dev'], { stdio: 'pipe' });
    let output = '';
    let error = '';
    proc.stdout.on('data', (data) => {
      output += data.toString();
      if (output.includes('Local:')) {
        proc.kill();
        resolve(output);
      }
    });
    proc.stderr.on('data', (data) => {
      error += data.toString();
    });
    proc.on('error', (err) => {
      reject(err);
    });
    proc.on('close', (code) => {
      if (!output.includes('Local:')) {
        reject(new Error('Dev server did not start. Output: ' + output + error));
      }
    });
  });
}

describe('Vite Dev Server', () => {
  it('should start successfully', async () => {
    const output = await runDevServer();
    expect(output).toMatch(/Local:/);
  }, 20000); // 20s timeout
});
