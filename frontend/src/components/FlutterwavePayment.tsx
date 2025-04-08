import React from "react";
import { WebView } from "react-native-webview";
import { ActivityIndicator, View } from "react-native";
import { useRoute, useNavigation, RouteProp } from "@react-navigation/native";
import { updateTransactionStatus } from "../src/api/updateTransactionStatus"; // Ensure correct API path

type RouteParams = {
  paymentUrl: string;
  transactionId: string;
};

const FlutterwavePayment: React.FC = () => {
  const route = useRoute<RouteProp<{ params: RouteParams }, "params">>();
  const navigation = useNavigation();

  const { paymentUrl, transactionId } = route.params;

  const handleNavigationChange = async (navState: { url: string }) => {
    const { url } = navState;

    if (url.includes("status=successful")) {
      await updateTransactionStatus(transactionId, "successful");
      navigation.replace("PaymentSuccess", { transactionId });
    } else if (url.includes("status=failed") || url.includes("status=cancelled")) {
      await updateTransactionStatus(transactionId, "failed");
      navigation.replace("FailureScreen", { transactionId });
    }
  };

  return (
    <View style={{ flex: 1 }}>
      <WebView
        source={{ uri: paymentUrl }}
        onNavigationStateChange={handleNavigationChange}
        startInLoadingState={true}
        renderLoading={() => (
          <ActivityIndicator
            size="large"
            color="#007bff"
            style={{ flex: 1, justifyContent: "center", alignItems: "center" }}
          />
        )}
      />
    </View>
  );
};

export default FlutterwavePayment;
