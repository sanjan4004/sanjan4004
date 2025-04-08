document.addEventListener("DOMContentLoaded", function () {
    const paymentMethodSelect = document.querySelector("select[name='payment_method']");
    const phoneNumberField = document.getElementById("phoneNumberField");
    const phoneNumberInput = document.getElementById("phone_number");
    const loadingIndicator = document.getElementById("loadingIndicator");
    const transactionForm = document.getElementById("transaction-form");
    const recipientSelect = document.getElementById("id_recipient");
    const countryField = document.getElementById("id_country");
    const mobileWalletField = document.getElementById("mobile_wallet_field");
    const bankAccountField = document.getElementById("bank_account_field");
    const cardPaymentFields = document.getElementById("card_payment_fields");
    const tokenField = document.getElementById("token_field");

    let recipientsData = window.recipientsData || [];

    function getCSRFToken() {
        let csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
        return csrfToken ? csrfToken.value : "";
    }

    function detectCardType(cardNumber) {
        const cardPatterns = {
            visa: /^4/,
            mastercard: /^5[1-5]/,
            amex: /^3[47]/,
            discover: /^6/,
        };
        for (const [card, pattern] of Object.entries(cardPatterns)) {
            if (pattern.test(cardNumber)) return card;
        }
        return "unknown";
    }

    function generateTransactionReference() {
        let timestamp = Date.now();
        let randomNum = Math.floor(1000 + Math.random() * 9000);
        return `WT_${timestamp}${randomNum}`;
    }

    function toggleFields() {
        if (!paymentMethodSelect) return;

        const selectedPayment = paymentMethodSelect.value;

        [phoneNumberField, mobileWalletField, bankAccountField, cardPaymentFields, tokenField].forEach(field => {
            if (field) field.classList.add("d-none");
        });

        if (selectedPayment === "M-Pesa" && phoneNumberField) {
            phoneNumberField.classList.remove("d-none");
            phoneNumberInput.setAttribute("required", "true");
        } else if (phoneNumberInput) {
            phoneNumberInput.removeAttribute("required");
            phoneNumberInput.value = "";
        }

        if (selectedPayment === "Bank Transfer" && bankAccountField) {
            bankAccountField.classList.remove("d-none");
        } else if (["Visa", "MasterCard", "Amex"].includes(selectedPayment) && cardPaymentFields) {
            cardPaymentFields.classList.remove("d-none");
        } else if (["Google Pay", "Apple Pay"].includes(selectedPayment) && tokenField) {
            tokenField.classList.remove("d-none");
        } else if (selectedPayment === "Mobile Wallet" && mobileWalletField) {
            mobileWalletField.classList.remove("d-none");
        }
    }

    if (paymentMethodSelect) {
        toggleFields();
        paymentMethodSelect.addEventListener("change", toggleFields);
    }

    if (phoneNumberInput) {
        phoneNumberInput.addEventListener("input", function () {
            if (paymentMethodSelect.value === "M-Pesa" && !phoneNumberInput.value.startsWith("+254")) {
                alert("M-Pesa phone number must start with +254");
                phoneNumberInput.value = "+254";
            }
        });
    }

    const cardNumberInput = document.getElementById("card_number");
    if (cardNumberInput) {
        cardNumberInput.addEventListener("input", function () {
            const cardType = detectCardType(cardNumberInput.value);
            if (cardType !== "unknown") {
                paymentMethodSelect.value = cardType.charAt(0).toUpperCase() + cardType.slice(1);
                toggleFields();
            }
        });
    }

    if (recipientSelect) {
        recipientSelect.addEventListener("change", function () {
            const selectedRecipientId = parseInt(recipientSelect.value, 10);
            const selectedRecipient = recipientsData.find(rec => rec.id === selectedRecipientId);

            if (selectedRecipient) {
                document.getElementById("id_amount").value = selectedRecipient.amount || "";
                document.getElementById("id_currency").value = selectedRecipient.currency || "";

                if (countryField) {
                    for (let i = 0; i < countryField.options.length; i++) {
                        if (countryField.options[i].text === selectedRecipient.country_name) {
                            countryField.selectedIndex = i;
                            break;
                        }
                    }
                }

                if (selectedRecipient.payment_method) {
                    paymentMethodSelect.value = selectedRecipient.payment_method;
                    toggleFields();
                }
            }
        });
    }

    if (transactionForm) {
        transactionForm.addEventListener("submit", function (event) {
            event.preventDefault();

            let formData = {
                recipient: document.getElementById("id_recipient")?.value.trim() || "",
                amount: document.getElementById("id_amount")?.value.trim() || "",
                currency: document.getElementById("id_currency")?.value.trim() || "",
                payment_method: document.getElementById("id_payment_method")?.value.trim() || "",
                country: countryField?.value.trim() || "",
                transaction_reference: generateTransactionReference(),
            };

            if (!formData.country) {
                alert("Invalid country selection. Please select a valid country.");
                return;
            }

            if (formData.payment_method === "M-Pesa" && !phoneNumberInput.value.trim()) {
                alert("Phone number is required for M-Pesa payments.");
                return;
            }

            if (formData.payment_method === "Bank Transfer") {
                formData.account_number = document.getElementById("id_account_number")?.value.trim() || "";
                formData.bank_name = document.getElementById("id_bank_name")?.value.trim() || "";

                if (!formData.account_number || !formData.bank_name) {
                    alert("Bank account number and bank name are required for bank transfers.");
                    return;
                }
            }

            console.log("Sending Payment Request:", JSON.stringify(formData, null, 2));

            if (loadingIndicator) loadingIndicator.style.display = "block";

            fetch("/WorldTtance/api/flutterwave/initiate-payment/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: JSON.stringify(formData),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Network error: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (loadingIndicator) loadingIndicator.style.display = "none";
                if (data.payment_link) {
                    setTimeout(() => {
                        window.location.href = data.payment_link;
                    }, 500);
                } else {
                    alert("Error processing payment: " + (data.error || "Unknown error"));
                }
            })
            .catch(error => {
                if (loadingIndicator) loadingIndicator.style.display = "none";
                console.error("Payment Request Error:", error);
                alert("Payment request failed. Please try again.");
            });
        });
    }
});
