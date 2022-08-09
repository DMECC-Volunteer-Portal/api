/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "../templates/**/*.html",
        "../static/js/*.js"
    ],
    theme: {
        fontFamily: {
            dmecc: ['Asparagus Sprouts', 'sans-serif']
        },
        extend: {
            backgroundImage: {
                'balls': "url('../img/bg.png')",
            },
        },
    },
    plugins: [],
}
