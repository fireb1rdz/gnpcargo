jQuery(function ($) {
    $('.select2').select2({
        width: '100%',
        theme: 'bootstrap-5',
        placeholder: 'Selecione uma opção',
        allowClear: true
    });

    const $form = $('form');

    const $typeField = $('#id_cpforcnpj');
    const $cpfField = $('#id_cpf');
    const $cnpjField = $('#id_cnpj');

    const $cpfWrapper = $('#cpf-field-wrapper');
    const $cnpjWrapper = $('#cnpj-field-wrapper');

    function normalizeType(value) {
        return $.trim((value || '').toString()).toUpperCase();
    }

    function enableField($field, $wrapper) {
        $field.prop('disabled', false).prop('readonly', false);
        $wrapper.show();
    }

    function disableField($field, $wrapper) {
        $field.val('');
        $field.prop('disabled', true).prop('readonly', true);
        $wrapper.hide();
    }

    function applyMasks() {
        if ($.fn.mask) {
            $cpfField.mask('000.000.000-00');
            $cnpjField.mask('00.000.000/0000-00');
        } else {
            console.warn('jQuery Mask não foi carregado.');
        }
    }

    function toggleDocumentFields() {
        const selectedType = normalizeType($typeField.val());

        if (selectedType === 'CPF' || selectedType === 'PF') {
            enableField($cpfField, $cpfWrapper);
            disableField($cnpjField, $cnpjWrapper);
        } else if (selectedType === 'CNPJ' || selectedType === 'PJ') {
            enableField($cnpjField, $cnpjWrapper);
            disableField($cpfField, $cpfWrapper);
        } else {
            disableField($cpfField, $cpfWrapper);
            disableField($cnpjField, $cnpjWrapper);
        }
    }

    function onlyDigits(value) {
        return (value || '').replace(/\D/g, '');
    }

    applyMasks();
    toggleDocumentFields();

    $form.on('submit', function () {
        $cpfField.val(onlyDigits($cpfField.val()));
        $cnpjField.val(onlyDigits($cnpjField.val()));
    });

    $typeField.on('change', function () {
        toggleDocumentFields();
    });
});