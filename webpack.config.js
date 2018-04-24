const outdir = __dirname + '/build';

module.exports = {
    entry: {
        // plugin: ['whatwg-fetch', './build/index.js'],
        standalone: ['whatwg-fetch', './build/standalone.js']
    },
    output: {
        path: __dirname + '/build',
        filename: '[name]-bundle.js',
        publicPath: './'
    },
    bail: true,
    mode: "development",
    devtool: 'cheap-source-map',
    module: {
        rules: [
            { test: /\.css$/, use: ['style-loader', 'css-loader'] },
            { test: /\.json$/, use: 'json-loader', exclude: /node_modules/ },
            { test: /\.html$/, use: 'file-loader' },
            { test: /\.md$/, use: 'raw-loader' },
            { test: /\.(jpg|png|gif)$/, use: 'file-loader' },
            { test: /\.js.map$/, use: 'file-loader' },
            { test: /\.woff2(\?v=\d+\.\d+\.\d+)?$/, use: 'url-loader?limit=10000&mimetype=application/font-woff' },
            { test: /\.woff(\?v=\d+\.\d+\.\d+)?$/, use: 'url-loader?limit=10000&mimetype=application/font-woff' },
            { test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/, use: 'url-loader?limit=10000&mimetype=application/octet-stream' },
            { test: /\.eot(\?v=\d+\.\d+\.\d+)?$/, use: 'file-loader' },
            { test: /\.svg(\?v=\d+\.\d+\.\d+)?$/, use: 'url-loader?limit=10000&mimetype=image/svg+xml' }
        ],
    }
};