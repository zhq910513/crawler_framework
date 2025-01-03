import com.google.gson.Gson;
import com.google.gson.JsonObject;
import okhttp3.*;
import java.io.IOException;
import java.util.*;

public class QF {
    private final OkHttpClient session;
    private final Gson gson;
    private Headers.Builder currentHeaders;

    public QF() {
        this.session = getSession();
        this.gson = new Gson();
        this.currentHeaders = new Headers.Builder();
        initializeHeaders(generateHeaders());
    }

    private void initializeHeaders(Map<String, String> headers) {
        for (Map.Entry<String, String> entry : headers.entrySet()) {
            currentHeaders.set(entry.getKey(), entry.getValue());
        }
    }

    private static Map<String, String> generateCookies() {
        try {
            return new HashMap<>();
        } catch (Exception e) {
            throw new RuntimeException("获取 cookies 失败: " + e.getMessage());
        }
    }

    private static Map<String, String> generateHeaders() {
        Map<String, String> headers = new HashMap<>();
        headers.put("Accept", "application/json, text/plain, */*");
        headers.put("Accept-Language", "zh-CN,zh;q=0.9");
        headers.put("Cache-Control", "no-cache");
        headers.put("Connection", "keep-alive");
        headers.put("Pragma", "no-cache");
        headers.put("Referer", "https://item-hk.qfapi.com/crp/");
        headers.put("Sec-Fetch-Dest", "empty");
        headers.put("Sec-Fetch-Mode", "cors");
        headers.put("Sec-Fetch-Site", "same-origin");
        headers.put("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36");
        headers.put("sec-ch-ua", "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"");
        headers.put("sec-ch-ua-mobile", "?0");
        headers.put("sec-ch-ua-platform", "\"Windows\"");
        return headers;
    }

    private static String acceptLink(String link) {
        return link.split("link_id=")[1].split("&")[0];
    }

    private OkHttpClient getSession() {
        return new OkHttpClient.Builder()
                .cookieJar(new CookieJar() {
                    private final HashMap<String, List<Cookie>> cookieStore = new HashMap<>();

                    @Override
                    public void saveFromResponse(HttpUrl url, List<Cookie> cookies) {
                        cookieStore.put(url.host(), cookies);
                    }

                    @Override
                    public List<Cookie> loadForRequest(HttpUrl url) {
                        List<Cookie> cookies = cookieStore.get(url.host());
                        return cookies != null ? cookies : new ArrayList<>();
                    }
                })
                .build();
    }

    private void updateHeaders(Map<String, String> headers) {
        currentHeaders = new Headers.Builder();
        for (Map.Entry<String, String> entry : headers.entrySet()) {
            currentHeaders.set(entry.getKey(), entry.getValue());
        }
    }

    private Map<String, String> getLinkBaseInfo(String link) throws IOException {
        String linkId = acceptLink(link);
        HttpUrl url = HttpUrl.parse("https://item-hk.qfapi.com/remotepay/pay/detail")
                .newBuilder()
                .addQueryParameter("link_id", linkId)
                .addQueryParameter("format", "cors")
                .build();

        Request request = new Request.Builder()
                .url(url)
                .headers(currentHeaders.build())
                .build();

        try (Response response = session.newCall(request).execute()) {
            String responseBody = response.body().string();
            JsonObject respJson = gson.fromJson(responseBody, JsonObject.class);
            JsonObject data = respJson.getAsJsonObject("data");
            JsonObject intendCustomer = data.getAsJsonObject("intend_customer");

            Map<String, String> customerInfo = new HashMap<>();
            customerInfo.put("link_id", data.get("link_id").getAsString());
            customerInfo.put("name", intendCustomer.get("name").getAsString());
            customerInfo.put("mobile", "");
            customerInfo.put("memo", "");
            customerInfo.put("email", "");
            customerInfo.put("detail", "");
            customerInfo.put("agree_pact", "2");
            customerInfo.put("customer_id", intendCustomer.get("customer_id").getAsString());
            customerInfo.put("address_id", "");
            customerInfo.put("return_url", "https://item-hk.qfapi.com/remotepay/pay/pay_result");
            customerInfo.put("failed_url", "https://item-hk.qfapi.com/remotepay/pay/pay_result");
            customerInfo.put("format", "cors");

            return customerInfo;
        }
    }

    private Map<String, String> submitFormForPayment(Map<String, String> data) throws IOException {
        Map<String, String> headers = new HashMap<>();
        headers.put("Accept", "application/json, text/plain, */*");
        headers.put("Accept-Language", "zh-CN,zh;q=0.9");
        headers.put("Cache-Control", "no-cache");
        headers.put("Connection", "keep-alive");
        headers.put("Content-Type", "application/x-www-form-urlencoded");
        headers.put("Origin", "https://item-hk.qfapi.com");
        headers.put("Pragma", "no-cache");
        headers.put("Referer", "https://item-hk.qfapi.com/crp/");
        headers.put("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36");
        headers.put("sec-ch-ua", "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"");
        headers.put("sec-ch-ua-mobile", "?0");
        headers.put("sec-ch-ua-platform", "\"Windows\"");

        updateHeaders(headers);

        FormBody.Builder formBuilder = new FormBody.Builder();
        for (Map.Entry<String, String> entry : data.entrySet()) {
            formBuilder.add(entry.getKey(), entry.getValue());
        }

        Request request = new Request.Builder()
                .url("https://item-hk.qfapi.com/remotepay/pay/do_order")
                .headers(currentHeaders.build())
                .post(formBuilder.build())
                .build();

        try (Response response = session.newCall(request).execute()) {
            String responseBody = response.body().string();
            JsonObject respJson = gson.fromJson(responseBody, JsonObject.class);
            JsonObject paymentInfo = respJson.getAsJsonObject("data").getAsJsonObject("pay");

            Map<String, String> result = new HashMap<>();
            for (Map.Entry<String, com.google.gson.JsonElement> entry : paymentInfo.entrySet()) {
                result.put(entry.getKey(), entry.getValue().getAsString());
            }
            result.put("txamt", paymentInfo.get("txamt").getAsString());

            return result;
        }
    }

    private void checkOutInfo(Map<String, String> data) throws IOException {
        Map<String, String> headers = new HashMap<>();
        headers.put("Accept", "application/json; charset=UTF-8");
        headers.put("Accept-Language", "zh-CN,zh;q=0.9");
        headers.put("Cache-Control", "no-cache");
        headers.put("Connection", "keep-alive");
        headers.put("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
        headers.put("Origin", "https://openapi-hk.qfapi.com");
        headers.put("Pragma", "no-cache");
        headers.put("Referer", "https://openapi-hk.qfapi.com/checkstand/");
        headers.put("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36");
        headers.put("sec-ch-ua", "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"");
        headers.put("sec-ch-ua-mobile", "?0");
        headers.put("sec-ch-ua-platform", "\"Windows\"");

        updateHeaders(headers);

        Map<String, String> newData = new HashMap<>(data);
        newData.put("lang", "zh-cn");
        newData.put("pay_env", "pc");
        newData.put("format", "cors");

        FormBody.Builder formBuilder = new FormBody.Builder();
        for (Map.Entry<String, String> entry : newData.entrySet()) {
            formBuilder.add(entry.getKey(), entry.getValue());
        }

        Request request = new Request.Builder()
                .url("https://openapi-hk.qfapi.com/checkout/v1/info")
                .headers(currentHeaders.build())
                .post(formBuilder.build())
                .build();

        try (Response response = session.newCall(request).execute()) {
            response.body().close();
        }
    }

    private String getPaymentLink(Map<String, String> data) throws IOException {
        Map<String, String> headers = new HashMap<>();
        headers.put("Accept", "application/json; charset=UTF-8");
        headers.put("Accept-Language", "zh-CN,zh;q=0.9");
        headers.put("Cache-Control", "no-cache");
        headers.put("Connection", "keep-alive");
        headers.put("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
        headers.put("Origin", "https://openapi-hk.qfapi.com");
        headers.put("Pragma", "no-cache");
        headers.put("Referer", "https://openapi-hk.qfapi.com/checkstand/");
        headers.put("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36");
        headers.put("sec-ch-ua", "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"");
        headers.put("sec-ch-ua-mobile", "?0");
        headers.put("sec-ch-ua-platform", "\"Windows\"");

        updateHeaders(headers);

        Map<String, String> newData = new HashMap<>(data);
        newData.put("pay_type", "801514");
        newData.put("format", "cors");
        newData.put("pay_tag", "ALIPAYCN");

        FormBody.Builder formBuilder = new FormBody.Builder();
        for (Map.Entry<String, String> entry : newData.entrySet()) {
            formBuilder.add(entry.getKey(), entry.getValue());
        }

        Request request = new Request.Builder()
                .url("https://openapi-hk.qfapi.com/checkout/v1/payment")
                .headers(currentHeaders.build())
                .post(formBuilder.build())
                .build();

        try (Response response = session.newCall(request).execute()) {
            String responseBody = response.body().string();
            JsonObject respJson = gson.fromJson(responseBody, JsonObject.class);
            return respJson.get("pay_url").getAsString();
        }
    }

    public String run(String link) throws IOException {
        Map<String, String> customerInfo = getLinkBaseInfo(link);
        Map<String, String> paymentInfo = submitFormForPayment(customerInfo);
        checkOutInfo(paymentInfo);
        return getPaymentLink(paymentInfo);
    }
}