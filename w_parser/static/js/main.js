document.addEventListener("DOMContentLoaded", () => {
    // сохранение
    const btn = document.getElementById("save-results");
    if (btn) {
        btn.addEventListener("click", () => {
            const products = Array.from(document.querySelectorAll("tbody tr"))
                .map(row => {
                    const cells = row.querySelectorAll("td");
                    const wbId = parseInt(row.dataset.wbId, 10);
                    if (isNaN(wbId)) return null;
                    return {
                        wb_id: wbId,
                        name: cells[0].innerText.trim(),
                        price: parseInt(cells[1].innerText.replace(/\D/g, "")) || 0,
                        discount_price: parseInt(cells[2].innerText.replace(/\D/g, "")) || 0,
                        rating: row.dataset.rating
                            ? parseFloat(row.dataset.rating.replace(",", "."))
                            : null,
                        reviews: parseInt(cells[4].innerText.replace(/\D/g, "")) || 0,
                    };
                })
                .filter(p => p !== null);

            fetch(saveUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({query, products}),
            })

                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        window.location = data.redirect;
                    } else {
                        alert("Ошибка: " + data.error);
                    }
                })
                .catch(err => {
                    alert("Сбой сети или сервера: " + err);
                });
        });
    }

    // гистограмма
    const canvas = document.getElementById('priceHistogramCanvas');
    let priceHistogramChart;
    if (canvas) {
        const rows = Array.from(document.querySelectorAll("tbody tr"));
        if (rows.length) {
            const prices = rows.map(r => {
                const cell = r.querySelector("td:nth-child(3)");
                return parseInt(cell ? cell.innerText.replace(/\D/g, "") : "0", 10) || 0;
            });
            const maxPrice = Math.max(...prices);
            const step = Math.ceil(maxPrice / 5) || 1;
            const priceBins = [0, step, step * 2, step * 3, step * 4, Infinity];
            const priceLabels = [
                `0–${step}`,
                `${step}–${step * 2}`,
                `${step * 2}–${step * 3}`,
                `${step * 3}–${step * 4}`,
                `${step * 4}+`
            ];

            const priceCounts = priceBins.slice(0, -1).map((_, i) => {
                const min = priceBins[i], max = priceBins[i + 1];
                return prices.filter(p => p >= min && p < max).length;
            });

            const ctx = canvas.getContext('2d');
            priceHistogramChart = new Chart(ctx, {
                type: 'bar',
                data: {labels: priceLabels, datasets: [{label: 'Количество товаров', data: priceCounts, backgroundColor: 'rgba(54, 162, 235, 0.5)', borderColor: 'rgba(54, 162, 235, 1)', borderWidth: 1}]},
                options: {scales: {x: {title: {display: true, text: 'Диапазон цены (₽)'}}, y: {title: {display: true, text: 'Число товаров'}, beginAtZero: true}}, plugins: {legend: {display: false}}}
            });
        }
    }

    function refreshPriceHistogram() {
        if (!canvas || !priceHistogramChart) return;
        const newRows = Array.from(document.querySelectorAll("tbody tr"));
        const newPrices = newRows.map(r => parseInt(r.querySelector("td:nth-child(3)").innerText.replace(/\D/g, ""), 10) || 0);
        const bins = priceHistogramChart.data.datasets[0].data.map((_, i) => i);
        const priceBins = priceHistogramChart.data.labels.map((label, i) => null);
        const origBins = priceHistogramChart.config.data.labels.map((_, i) => i);
        const maxP = Math.max(...newPrices);
        const step = Math.ceil(maxP / 5) || 1;
        const binsArr = [0, step, step * 2, step * 3, step * 4, Infinity];
        const newCounts = binsArr.slice(0, -1).map((_, i) => newPrices.filter(p => p >= binsArr[i] && p < binsArr[i + 1]).length);
        priceHistogramChart.data.datasets[0].data = newCounts;
        priceHistogramChart.update();
    }

    document.querySelectorAll('input[name="min_price"], input[name="max_price"], input[name="min_rating"], input[name="min_reviews"], select[name="sort_by"]').forEach(el => el.addEventListener('change', refreshPriceHistogram));

    // скидка / рейтинг
    const canvas2 = document.getElementById('discountRatingCanvas');
    let discountRatingChart;
    if (canvas2) {
        const buildData = () => {
            const rows = Array.from(document.querySelectorAll("tbody tr"));
            return rows.map(r => {
                const cells = r.querySelectorAll("td");
                const full = parseInt(cells[1].innerText.replace(/\D/g, ""), 10) || 0;
                const disc = parseInt(cells[2].innerText.replace(/\D/g, ""), 10) || 0;
                const rating = parseFloat(r.dataset.rating) || 0;
                return {x: full - disc, y: rating};
            }).sort((a, b) => a.x - b.x);
        };
        const drCtx = canvas2.getContext('2d');
        discountRatingChart = new Chart(drCtx, {
            type: 'line',
            data: {datasets: [{label: 'Скидка vs Рейтинг', data: buildData(), fill: false, tension: 0.2, borderColor: 'rgba(255,99,132,1)', pointBackgroundColor: 'rgba(255,99,132,0.8)'}]},
            options: {scales: {x: {type: 'linear', title: {display: true, text: 'Размер скидки (₽)'}}, y: {title: {display: true, text: 'Рейтинг'}, suggestedMin: 0, suggestedMax: 5}}, plugins: {legend: {display: false}}}
        });
    }

    function refreshDiscountChart() {
        if (!canvas2 || !discountRatingChart) return;
        discountRatingChart.data.datasets[0].data = Array.from(document.querySelectorAll("tbody tr")).map(r => {
            const cells = r.querySelectorAll("td");
            const full = parseInt(cells[1].innerText.replace(/\D/g, ""), 10) || 0;
            const disc = parseInt(cells[2].innerText.replace(/\D/g, ""), 10) || 0;
            const rating = parseFloat(r.dataset.rating) || 0;
            return {x: full - disc, y: rating};
        }).sort((a, b) => a.x - b.x);
        discountRatingChart.update();
    }

    document.querySelectorAll('input[name="min_price"], input[name="max_price"], input[name="min_rating"], input[name="min_reviews"], select[name="sort_by"]').forEach(el => el.addEventListener('change', refreshDiscountChart));

    document.addEventListener('click', e => {
        if (e.target.matches('button[data-bs-dismiss="alert"]')) {
            const alertEl = e.target.closest('.alert');
            if (alertEl) alertEl.remove();
        }
    });

    // потягушки цен
    const priceInputs = document.querySelectorAll('.filter__price-inputs .filter__input');
    const rangeInputs = document.querySelectorAll('.filter__range-inputs input[type="range"]');
    const progressBar = document.querySelector('.filter__slider .filter__progress');
    if (priceInputs.length === 2 && rangeInputs.length === 2 && progressBar) {
        const maxRangeVal = parseInt(rangeInputs[0].max, 10) || 0;
        const priceGap = 1;
        const syncAll = (minVal, maxVal) => {
            rangeInputs[0].value = minVal;
            rangeInputs[1].value = maxVal;
            progressBar.style.left = `calc(${(minVal / maxRangeVal) * 100}% - 0.5rem)`;
            progressBar.style.right = `calc(${(100 - (maxVal / maxRangeVal) * 100)}% - 0.5rem)`;
            priceInputs[0].value = minVal;
            priceInputs[1].value = maxVal;
        };
        let initMin = parseInt(priceInputs[0].value, 10) || 0;
        let initMax = parseInt(priceInputs[1].value, 10);
        if (isNaN(initMax)) initMax = maxRangeVal;
        syncAll(initMin, initMax);
        priceInputs.forEach((inp, idx) => inp.addEventListener('input', () => {
            let minVal = parseInt(priceInputs[0].value, 10) || 0;
            let maxVal = parseInt(priceInputs[1].value, 10) || maxRangeVal;
            if (maxVal - minVal < priceGap) idx === 0 ? minVal = maxVal - priceGap : maxVal = minVal + priceGap;
            syncAll(minVal, maxVal);
        }));
        rangeInputs.forEach((inp, idx) => inp.addEventListener('input', () => {
            let minVal = parseInt(rangeInputs[0].value, 10);
            let maxVal = parseInt(rangeInputs[1].value, 10);
            if (maxVal - minVal < priceGap) idx === 0 ? minVal = maxVal - priceGap : maxVal = minVal + priceGap;
            syncAll(minVal, maxVal);
        }));
    }
});
