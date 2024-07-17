document.getElementById('SelectBankerPaymentType').addEventListener('change', function() {
    var value = this.value;

    var pixInputs = document.getElementById('pixInputs');
    pixInputs.style.display = (value === 'pix') ? 'block' : 'none';
    Array.from(pixInputs.querySelectorAll('input')).forEach(input => {
        input.disabled = (value !== 'pix');
    });

    var creditAccountInputs = document.getElementById('creditAccountInputs');
    creditAccountInputs.style.display = (value === 'credito-conta') ? 'block' : 'none';
    Array.from(creditAccountInputs.querySelectorAll('input')).forEach(input => {
        input.disabled = (value !== 'credito-conta');
    });

    var orderPaymentInputs = document.getElementById('orderPaymentInputs');
    orderPaymentInputs.style.display = (value === 'ordempagamento') ? 'block' : 'none';
    Array.from(orderPaymentInputs.querySelectorAll('input')).forEach(input => {
        input.disabled = (value !== 'ordempagamento');
    });
});
