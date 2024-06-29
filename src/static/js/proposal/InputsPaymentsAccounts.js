document.getElementById('SelectBankerPayment').addEventListener('change', function() {
    var value = this.value;
    document.getElementById('pixInputs').style.display = (value === 'pix') ? 'block' : 'none';
    document.getElementById('creditAccountInputs').style.display = (value === 'credito-conta') ? 'block' : 'none';
    document.getElementById('orderPaymentInputs').style.display = (value === 'ordempagamento') ? 'block' : 'none';
});