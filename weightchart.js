$(document).ready(function() {
    //$.get('http://127.0.0.1:8000/output.csv', function (data) {
    $.get('output.csv', function (data) {
        Highcharts.setOptions({
            global: {
                useUTC: true
            },
            colors: ['#2222ff', '#ff2222']
        });
        $('#container').highcharts({

            chart: {
                defaultSeriesType: 'spline',
                zoomType: 'x'
            },
            data: {
                csv: data
            },
            xAxis: {
                type: 'datetime',
                dateTimeLabelFormats: {
                    month: '%b %e',
                    year: '%b'
                },
                title: {
                    text: 'Date'
                }
            },
            yAxis: {
                title: {
                    text: "Weight (lbs)"
                }
            },
            plotOptions: {
                series: {
                    shadow: true,
                    connectNulls: true,
                    marker: {
                        enabled: false
                    }
                }
            },
            title: {
                text: "Weight (lbs) vs. Time"
            },
            subtitle: {
                text: null
            }
        });
    }); 
});
