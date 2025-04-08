import React from "react";
import { View, Text, Button, StyleSheet } from "react-native";
import { useNavigation } from "@react-navigation/native";
import { StackNavigationProp } from "@react-navigation/stack";
import { RootStackParamList } from "../../App";

// Define navigation type for the HomeScreen
type HomeScreenNavigationProp = StackNavigationProp<RootStackParamList, "Home">;

const HomeScreen: React.FC = () => {
    const navigation = useNavigation<HomeScreenNavigationProp>();

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Welcome to WorldTtance</Text>
            <Text style={styles.subtitle}>Send money safely and securely.</Text>
            <Button
                title="Make a Payment"
                onPress={() => navigation.navigate("PaymentScreen")}
                color="#007bff"
                accessibilityLabel="Navigate to payment screen"
            />
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "#f4f4f4",
        padding: 20,
    },
    title: {
        fontSize: 28,
        fontWeight: "bold",
        color: "#007bff",
        marginBottom: 20,
        textAlign: "center",
    },
    subtitle: {
        fontSize: 18,
        color: "#333",
        marginBottom: 30,
        textAlign: "center",
    },
});

export default HomeScreen;
