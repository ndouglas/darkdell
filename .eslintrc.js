module.exports = {
  root: true,
  env: {
    browser: true,
    mocha: true
  },
  globals: {
    expect: true
  },
  overrides: [
    {
      files: ['*.html'],
      parser: '@html-eslint/parser',
      extends: ['plugin:@html-eslint/recommended'],
      rules: {
        '@html-eslint/indent': ['error', 2],
        '@html-eslint/require-doctype': 'off',
        'spaced-comment': 'off'
      }
    }
  ],
  plugins: ['@html-eslint'],
  extends: [
    'eslint-config-standard'
  ],
  ignorePatterns: [
    '.yarn/**',
    'dist/**',
    'vendor/**',
    'node_modules/**',
    'public/**'
  ],
  rules: {
    indent: ['error', 2],
    'no-use-before-define': ['error', { functions: false, classes: true, variables: true }]
  }
}
