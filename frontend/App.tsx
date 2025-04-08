import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { LogBox } from 'react-native';

import HomeScreen from './src/screens/HomeScreen';
import PaymentScreen from './src/screens/PaymentScreen';
import WebViewScreen from './src/screens/WebViewScreen';
import PaymentSuccess from './src/screens/PaymentSuccess';
import FailureScreen from './src/screens/FailureScreen';
import SuccessScreen from './src/screens/SuccessScreen';
import CheckoutScreen from './src/screens/CheckoutScreen';

// Ignore specific warnings (optional, for debugging)
LogBox.ignoreAllLogs(false);
LogBox.ignoreLogs(["Warning: ..."]); // Ignore specific warnings

// Define navigation stack types
export type RootStackParamList = {
  Home: undefined;
  PaymentScreen: undefined;
  WebViewScreen: { url: string };
  PaymentSuccess: { transactionId: string };  // include transactionId
};

const Stack = createNativeStackNavigator<RootStackParamList>();

const App = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerStyle: { backgroundColor: "#007bff" },
          headerTintColor: "#fff",
          headerTitleStyle: { fontWeight: "bold" },
        }}
      >
        <Stack.Screen name="Home" component={HomeScreen} options={{ title: "Welcome to WorldTtance" }} />
        <Stack.Screen name="PaymentScreen" component={PaymentScreen} options={{ title: "Make a Payment" }} />
        <Stack.Screen name="WebViewScreen" component={WebViewScreen} options={{ title: "Processing Payment" }} />
        <Stack.Screen name="PaymentSuccess" component={PaymentSuccess} options={{ title: "Payment Successful" }} />
        <Stack.Screen name="FailureScreen" component={FailureScreen} options={{ title: "Payment Failed" }} />
        <Stack.Screen name="SuccessScreen" component={SuccessScreen} options={{ title: "Success Screen" }} />
        <Stack.Screen name="CheckoutScreen" component={CheckoutScreen} options={{ title: "Checkout" }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default App;
