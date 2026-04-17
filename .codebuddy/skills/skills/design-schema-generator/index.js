#!/usr/bin/env node

const DesignSchemaGenerator = require('./src/index.js');

async function main() {
  const generator = new DesignSchemaGenerator();
  await generator.start();
}

main();