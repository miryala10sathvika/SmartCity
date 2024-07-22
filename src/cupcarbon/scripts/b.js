const {execSync} = require('child_process');

while (true) {
  console.log("print Hello")
  console.log("mark")
  execSync('sleep 1')
  console.log("print World !")
  console.log("unmark")
  execSync('sleep 1')
}
