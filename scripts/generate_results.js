const fs = require('fs');
const path = require('path');

function *walkSync(dir) {
  const files = fs.readdirSync(dir, { withFileTypes: true });
  for (const file of files) {
    if (file.isDirectory()) {
      yield* walkSync(path.join(dir, file.name));
    } else {
      if (file.name.indexOf('plot.json')>-1) {
          yield path.relative('./',path.join(dir, file.name));
      }
    }
  }
}

const result = {

}
for (const filePath of walkSync('../docs/')) {
    const [, , ref, dates, timeframe] = filePath.split('\\')
    const [date_init, date_end] = dates.split('_')
    let rawdata = fs.readFileSync(filePath);
    if (!result[ref]){
      result[ref] = {}
    }
    if (!result[ref][timeframe]){
      result[ref][timeframe] = []
    }
    result[ref][timeframe].push({
      date_init,
      date_end,
      data: JSON.parse(rawdata)
    })
}
let data = JSON.stringify(result);
fs.writeFileSync('../docs/results.json', data);