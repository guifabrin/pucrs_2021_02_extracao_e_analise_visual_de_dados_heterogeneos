const fs = require('fs');
const path = require('path');

function *walkSync(dir) {
  const files = fs.readdirSync(dir, { withFileTypes: true });
  for (const file of files) {
    if (file.isDirectory()) {
      yield* walkSync(path.join(dir, file.name));
    } else {
      if (file.name.indexOf('plot.html')>-1) {
          yield path.relative('./',path.join(dir, file.name));
      }
    }
  }
}

const result = []
for (const filePath of walkSync(__dirname)) {
  result.push(filePath)
}
let data = JSON.stringify(result);
fs.writeFileSync('plots.json', data);