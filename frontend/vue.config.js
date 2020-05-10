module.exports = {
    devServer: {
        proxy: {
            "^/ws": {
                target: "http://localhost:4999",
                ws: true,
                secure: false
            }
        }
    }
};