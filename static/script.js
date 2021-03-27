function splitscroll() {
    const controller = new ScrollMagic.Controller()

    // Songs
    new ScrollMagic.Scene({
        duration: '300%',
        triggerElement: '.title',
        triggerHook: 0
    })
        .setPin('.title')
        .addTo(controller)

    // Artists
    new ScrollMagic.Scene({
        duration: '300%',
        triggerElement: '.title2',
        triggerHook: 0
    })
        .setPin('.title2')
        .addTo(controller)

    // Genres
    new ScrollMagic.Scene({
        duration: '100%',
        triggerElement: '.title3',
        triggerHook: 0
    })
        .setPin('.title3')
        .addTo(controller)

    // Recommended Artists
    new ScrollMagic.Scene({
        duration: '100%',
        triggerElement: '.title4',
        triggerHook: 0
    })
        .setPin('.title4')
        .addTo(controller)

    // Recommended Songs
    new ScrollMagic.Scene({
        duration: '100%',
        triggerElement: '.title5',
        triggerHook: 0
    })
        .setPin('.title5')
        .addTo(controller)

    // Radar Chart
    new ScrollMagic.Scene({
        duration: '150%',
        triggerElement: '#chart',
        triggerHook: 0
    })
        .setPin('#chart')
        .addTo(controller)

}

splitscroll()

function radarChart(columns, values) {
    options = {
        chart: {
            type: 'radar',
        },
        series: [
            {
                name: "Value",
                data: values
            },
        ],
        xaxis: {
            categories: columns,
            labels: {
                show: true,
                style: {
                    colors: ['#ffffff', '#ffffff', '#ffffff', '#ffffff', '#ffffff', '#ffffff', '#ffffff',],
                    fontSize: '20px',
                    fontFamily: 'Montserrat'
                }
            }
        },
        yaxis: {
            show: false,
            min: 0,
            max: 1,
        },
        plotOptions: {
            radar: {
                polygons: {
                    strokeColor: '#ffffff',
                }
            }
        },
        fill: {
            opacity: 0.8,
            colors: ['#fff']
        },
        stroke: {
            show: true,
            width: 4,
            colors: ['#000'],
            dashArray: 0
        },
        dataLabels: {
            enabled: true,
            background: {
                enabled: true,
                foreColor: '#fff',
                borderRadius: 5,
                padding: 4,
            },
            style: {
                colors: ['#000'],
                fontFamily: 'Montserrat',
            }
        },
    }

    return options
}

function tempoChart(tempo) {
    options = {
        chart: {
            type: 'radialBar'
        },
        title: {
            text: 'Tempo (Beats Per Minute) of Songs',
            align: 'center',
            style : {
                fontFamily: 'Montserrat',
                fontSize: '25px',
                color: '#fff'
            }
        },
        series: tempo,
        colors: ['#FD552C', '#FF7756', '#FEB29F'],
        plotOptions: {
            radialBar: {
                dataLabels: {
                    name: {
                        show: true,
                        fontSize: '20px',
                        fontFamily: 'Montserrat'
                    },
                    value: {
                        show: true,
                        fontSize: '20px',
                        formatter: function (val) {
                            return val * 2 + 'bpm'
                        },
                        fontFamily: 'Montserrat',
                        color: '#fff'
                    },
                    total: {
                        show: true,
                        label: 'Tempo (BPM)',
                        formatter: function (val) {
                            return ''
                        },
                        fontSize: '20px',
                        fontFamily: 'Montserrat',
                        color: '#fff'
                    },
                    
                },
                track: {
                    background: '#fff'
                }
            }
        },
        labels: ['Highest Tempo', 'Average Tempo', 'Lowest Tempo']
    }

    return options
}

function songArtist(all_artists, songs) {
    options = {
        chart: {
            height: window.innerHeight,
            type: "treemap",
        },
        title: {
            text: `See how different Artists contribute to your Top ${songs.length} Songs`,
            align: 'center',
            style : {
                fontFamily: 'Montserrat',
                fontSize: '25px',
                color: '#fff'
            }
        },
        colors: ['#FF3200', '#FF8900', '#5200FF', '#FF0099'],
        series: [
            {
                data: all_artists,
            },
        ],
        dataLabels: {
            enabled: true,
            style: {
                fontSize: '20px',
                fontFamily: 'Montserrat',
            },
            formatter: function(text, op) {
                return [text, (op.value > 1 ? op.value + ' songs' : op.value + ' song')]
            }
        },
        // colors: ['#FD6540'],
        plotOptions: {
            treemap: {
                distributed: true
            }
        }
    }
    return options
}

function timeChart(duration) {
    options = {
        title: {
            text: 'Duration Of Songs',
            align: 'center',
            style : {
                fontFamily: 'Montserrat',
                fontSize: '25px',
                color: '#fff'
            }
        },
        colors: ['#FF8900', '#FFAD24', '#FFC058'],
        series: [{
            data: duration[1],
            name: 'Duration of Song in seconds'
        }],
        chart: {
            type: 'bar',
            height: 500,
            foreColor: '#fff',
            fontFamily: 'Montserrat'
        },
        plotOptions: {
            bar: {
                horizontal: true,
            }
        },
        dataLabels: {
            enabled: false,
            
        },
        xaxis: {
            categories: ['Longest', 'Average', 'Shortest'],
        }
    }

    return options
}

window.addEventListener('resize', () => {
    if (window.innerWidth < 768) {
        alert('Sorry We don\'t support Mobile Screens as of now')
    }
})