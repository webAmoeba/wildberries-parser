module.exports = {
    plugins: [
        require('postcss-import'),
        require('postcss-discard-comments')({removeAll: true}),
        require('postcss-url')({
            url: ({url}) => {
                return url.replace('../../', '../');
            },
        }),
    ],
};
