import dotenv from "dotenv";


async function main() {
    dotenv.config();

    console.log("Hello, World!");
}

(async () => {
    await main();
})();
