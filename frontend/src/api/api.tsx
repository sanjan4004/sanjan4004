const DJANGO_API_BASE_URL = "https://worldttance.com/WorldTtance";
const NODE_API_BASE_URL = "https://worldttance.com/node"; // Replace with your deployed Node.js API base path

// Unified API request function
const makeApiRequest = async (baseURL, url, method = "GET", data = null, userToken = null) => {
    try {
        const headers: { [key: string]: string } = {
            "Content-Type": "application/json",
        };

        if (userToken) {
            headers["Authorization"] = `Bearer ${userToken}`;
        }

        const response = await fetch(`${baseURL}${url}`, {
            method,
            headers,
            body: data ? JSON.stringify(data) : undefined,
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch: ${response.statusText}`);
        }

        const responseData = await response.json();
        if (!responseData) {
            throw new Error("No data received from the server.");
        }

        return responseData;
    } catch (error) {
        console.error("API request error:", error);
        return { error: error.message || "An error occurred while processing the request" };
    }
};

// 🌍 Initiate Payment via Node.js
export const initiateFlutterwavePayment = async (paymentData) => {
    return makeApiRequest(NODE_API_BASE_URL, "/pay", "POST", paymentData);
};

// 🔄 Update Transaction Status via Django
export const updateTransaction = async (transactionData, userToken) => {
    return makeApiRequest(DJANGO_API_BASE_URL, "/api/update-transaction", "POST", transactionData, userToken);
};

// 🛠️ Check Transaction Status via Django
export const checkTransactionStatus = async (transactionId) => {
    return makeApiRequest(DJANGO_API_BASE_URL, `/api/flutterwave/status${transactionId}/`, "GET");
};

// 🛠️ Updated Check Transaction Status via Django with new endpoint
export const checkTransactionStatusUpdated = async (transactionId) => {
    return makeApiRequest(DJANGO_API_BASE_URL, `/transaction-status${transactionId}/`, "GET");
};
