import React from "react";
import { View, ActivityIndicator, StyleSheet } from "react-native";
import { WebView } from "react-native-webview";
import { RouteProp, useNavigation } from "@react-navigation/native";
import { StackNavigationProp } from "@react-navigation/stack";
import { RootStackParamList } from "../App";
import { updateTransaction } from "../src/api/api/updateTransaction"; // Ensure correct API import

type WebViewScreenRouteProp = RouteProp<RootStackParamList, "WebViewScreen">;
type WebViewScreenNavigationProp = StackNavigationProp<RootStackParamList, "WebViewScreen">;

type Props = { route: WebViewScreenRouteProp };

const WebViewScreen: React.FC<Props> = ({ route }) => {
    const { url, transactionId } = route.params as { url: string; transactionId: string };
    const navigation = useNavigation<WebViewScreenNavigationProp>();

    // Handle navigation state change to detect success or failure
    const handleNavigationStateChange = async (navState: { url: string }) => {
        const successUrl = "http://worldttance.com/WorldTtance/transaction/success"; // Updated domain for success
        const failureUrl = "http://worldttance.com/WorldTtance/transaction/failed"; // Updated domain for failure

        // Check if the URL contains the success or failure endpoint
        if (navState.url.includes(successUrl)) {
            console.log("Payment Successful!");
            await updateTransaction({ transaction_id: transactionId, status: "successful" });
            navigation.replace("PaymentSuccess", { transactionId });
        } else if (navState.url.includes(failureUrl)) {
            console.log("Payment Failed.");
            await updateTransaction({ transaction_id: transactionId, status: "failed" });
            navigation.replace("PaymentFailure", { transactionId });
        }
    };

    return (
        <View style={styles.container}>
            <WebView
                source={{ uri: url }}
                startInLoadingState
                renderLoading={() => <ActivityIndicator size="large" color="#1E90FF" />}
                onNavigationStateChange={handleNavigationStateChange}
            />
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
});

export default WebViewScreen;
