module.exports = {
  root: true,
  env: {
    browser: true,
    mocha: true,
  },
  globals: {
    expect: true,
  },
  overrides: [
    {
      files: ["public/**/*.html"],
      parser: "@html-eslint/parser",
      extends: ["plugin:@html-eslint/recommended"],
      rules: {
        "@html-eslint/require-closing-tags": "off",
        "@html-eslint/no-multiple-empty-lines": [
          "error",
          {
            max: 0,
          },
        ],
        "@html-eslint/indent": ["error", 2],
        "spaced-comment": "off",
      },
    },
    {
      files: ["themes/darkdell/layouts/**/*.html"],
      parser: "@html-eslint/parser",
      extends: ["plugin:@html-eslint/recommended"],
      rules: {
        "@html-eslint/indent": "off",
        "@html-eslint/require-doctype": "off",
        "spaced-comment": "off",
      },
    },
  ],
  plugins: ["@html-eslint"],
  extends: ["eslint-config-standard", "plugin:prettier/recommended"],
  ignorePatterns: [".yarn/**", "dist/**", "vendor/**", "node_modules/**"],
  rules: {
    indent: ["error", 2],
    "no-use-before-define": [
      "error",
      { functions: false, classes: true, variables: true },
    ],
  },
};
