import axios from "axios";
import { REACT_APP_DJANGO_API_URL } from "./config"; // Ensure API base URL is correct

// Define the expected response type (adjust based on actual API response)
interface TransactionUpdateResponse {
    success: boolean;
    message?: string;
}

export const updateTransactionStatus = async (
    transactionId: string, 
    status: "successful" | "failed" | "pending"
): Promise<TransactionUpdateResponse | null> => {
    try {
        const response = await axios.post<TransactionUpdateResponse>(`${REACT_APP_DJANGO_API_URL}/api/update-transaction`, {
            transaction_id: transactionId,
            status: status,
        });

        return response.data;
    } catch (error) {
        console.error("Error updating transaction status:", error);
        return null;
    }
};
