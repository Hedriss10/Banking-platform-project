document.addEventListener('DOMContentLoaded', function () {
    var proposalForm = document.getElementById('proposalForm');

    proposalForm.addEventListener('submit', function (event) {
        event.preventDefault();

        var formData = new FormData(proposalForm);

        var fileFields = [
            'rg_cnh_completo[]',
            'contracheque[]',
            'extrato_consignacoes[]',
            'comprovante_residencia[]',
            'selfie[]',
            'comprovante_bancario[]',
            'detalhamento_inss[]',
            'historico_consignacoes_inss[]'
        ];

        var fileData = new FormData();

        fileFields.forEach(function(fieldName) {
            var files = formData.getAll(fieldName);
            if (files.length > 0) {
                files.forEach(function(file) {
                    fileData.append(fieldName, file);
                });
                formData.delete(fieldName);
            }
        });

        var formObject = {};
        formData.forEach(function(value, key){
            formObject[key] = value;
        });

        var jsonString = JSON.stringify(formObject);

        var aesKey = crypto.getRandomValues(new Uint8Array(32));

        var iv = crypto.getRandomValues(new Uint8Array(16));

        encryptAESGCM(jsonString, aesKey, iv).then(function(encryptedData) {
            var aesKeyBase64 = arrayBufferToBase64(aesKey);
            var ivBase64 = arrayBufferToBase64(iv);

            importRSAPublicKey(publicKeyPEM).then(function(publicKey) {
                window.crypto.subtle.encrypt(
                    {
                        name: "RSA-OAEP"
                    },
                    publicKey,
                    aesKey
                ).then(function(encryptedAESKey) {
                    var encryptedAESKeyBase64 = arrayBufferToBase64(new Uint8Array(encryptedAESKey));
                    var encryptedDataBase64 = arrayBufferToBase64(new Uint8Array(encryptedData));

                    fileData.append('encrypted_data', encryptedDataBase64);
                    fileData.append('encrypted_key', encryptedAESKeyBase64);
                    fileData.append('iv', ivBase64);

                    fetch('/proposal/new-proposal', {
                        method: 'POST',
                        body: fileData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('Contrato registrado com sucesso!');
                            window.location.href = "/home"
                        } else {
                            alert(data.message || 'Erro ao registrar o contrato.');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Erro ao enviar o formulário.');
                    });
                }).catch(function(err) {
                    console.error('Erro ao criptografar a chave AES:', err);
                    alert('Erro ao criptografar a chave AES.');
                });
            }).catch(function(err) {
                console.error('Erro ao importar a chave pública RSA:', err);
                alert('Erro ao importar a chave pública.');
            });
        }).catch(function(err) {
            console.error('Erro ao criptografar os dados:', err);
            alert('Erro ao criptografar os dados do formulário.');
        });
    });

    function pemToArrayBuffer(pem) {
        var b64Lines = pem.replace(/-----.*?-----/g, '').replace(/\n/g, '');
        var b64Decoded = atob(b64Lines);
        var arrayBuffer = new Uint8Array(b64Decoded.length);
        for (var i = 0; i < b64Decoded.length; i++) {
            arrayBuffer[i] = b64Decoded.charCodeAt(i);
        }
        return arrayBuffer.buffer;
    }

    function importRSAPublicKey(pemKey) {
        return new Promise(function(resolve, reject) {
            var binaryDer = pemToArrayBuffer(pemKey);
            window.crypto.subtle.importKey(
                "spki",
                binaryDer,
                {
                    name: "RSA-OAEP",
                    hash: "SHA-256"
                },
                true,
                ["encrypt"]
            ).then(function(publicKey) {
                resolve(publicKey);
            }).catch(function(err) {
                reject(err);
            });
        });
    }

    function encryptAESGCM(plaintext, key, iv) {
        var enc = new TextEncoder();
        var encodedText = enc.encode(plaintext);
        // Importar a chave AES para o formato CryptoKey
        return window.crypto.subtle.importKey(
            "raw",
            key,
            {
                name: "AES-GCM"
            },
            false,
            ["encrypt"]
        ).then(function(cryptoKey) {
            // Usar a chave importada para criptografar os dados
            return window.crypto.subtle.encrypt(
                {
                    name: "AES-GCM",
                    iv: iv
                },
                cryptoKey,
                encodedText
            );
        });
    }

    // Função para converter ArrayBuffer em Base64
    function arrayBufferToBase64(buffer) {
        var binary = '';
        var bytes = new Uint8Array(buffer);
        var len = bytes.byteLength;
        for (var i = 0; i < len; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    }
});
