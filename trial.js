const WITNESS_RESERVED_VALUE = Buffer.from(
    '0000000000000000000000000000000000000000000000000000000000000000',
    'hex',
)

// print(WITNESS_RESERVED_VALUE)
console.log(typeof WITNESS_RESERVED_VALUE)
console.log(WITNESS_RESERVED_VALUE.toString('hex'));


const str = WITNESS_RESERVED_VALUE.toString('hex');
let count = 0;

for (let i = 0; i < str.length; i++) {
    if (str[i] === '0') {
        count++;
    }
}

console.log("Number of zeros:", count);