import java.io.IOException;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

public class ProductSalesMapper
        extends Mapper<Object, Text, Text, IntWritable> {

    private final Text productId = new Text();
    private final IntWritable quantity = new IntWritable();

    @Override
    public void map(Object key, Text value, Context context)
            throws IOException, InterruptedException {

        String line = value.toString().trim();

        // Skip empty lines
        if (line.isEmpty()) {
            return;
        }

        // Skip CSV header
        if (line.startsWith("event_time")) {
            return;
        }

        String[] fields = line.split(",", -1);

        // Expected:
        // 0 = event_time
        // 1 = order_id
        // 2 = product_id
        // 3 = product_name
        // 4 = quantity

        if (fields.length < 5) {
            return;
        }

        String product = fields[2].trim();
        String qty = fields[4].trim();

        try {
            int q = Integer.parseInt(qty);

            productId.set(product);
            quantity.set(q);

            context.write(productId, quantity);

        } catch (NumberFormatException e) {
            // Ignore invalid records
        }
    }
}