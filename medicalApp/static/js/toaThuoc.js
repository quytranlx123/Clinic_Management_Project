function addThuocInToaThuoc(id, tenThuoc, giaBan) {
    event.preventDefault()

    fetch('/api/add-thuoc', {
        method: 'post',
        body: JSON.stringify({
            'id': id,
            'tenThuoc': tenThuoc,
            'giaBan': giaBan
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res) {
        console.info(res)
        return res.json()
    }).then(function(data) {
        console.info(data)

        let counter = document.getElementById('count-Loai-thuoc')
        counter.innerText = data.totalThuocQuantity
    }).catch(function(err) {
        console.error(err)
    })
}